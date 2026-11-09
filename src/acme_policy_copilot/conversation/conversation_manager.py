
import uuid
import json

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import sessionmaker

from langchain_core.messages import HumanMessage, AIMessage

from redis.exceptions import RedisError

from ..database.connection import SessionLocal
from ..database.models import User, Conversation, Message
from ..cache.redis_client import redis_client
from ..logger import logger


class ConversationManager:

    CACHE_TTL = 3600
    HISTORY_LIMIT = 20

    def __init__(self, session_factory: sessionmaker = SessionLocal):
        self.session_factory = session_factory

    # --------------------------------------------------
    # Redis cache helpers
    # --------------------------------------------------

    def _cache_key(self, conversation_id: uuid.UUID) -> str:
        return f"acme:conversation:{conversation_id}:history"

    def _invalidate_history_cache(self, conversation_id: uuid.UUID):
        try:
            redis_client.delete(self._cache_key(conversation_id))
        except RedisError:
            logger.exception(
                "Could not invalidate Redis history cache"
            )

    # --------------------------------------------------
    # 1. Find existing user or create new user
    # --------------------------------------------------

    def get_or_create_user(self, email: str, name: str):

        with self.session_factory() as db:
            with db.begin():

                user = db.scalar(
                    select(User).where(User.email == email)
                )

                if user is None:
                    user = User(
                        email=email,
                        name=name,
                    )

                    db.add(user)
                    db.flush()

                    logger.info(f"Created user: {email}")

                return user.user_id

    # --------------------------------------------------
    # 2. Create a new conversation
    # --------------------------------------------------

    def create_conversation(
        self,
        user_id: uuid.UUID,
        title: str | None = None,
    ):

        with self.session_factory() as db:
            with db.begin():

                user = db.get(User, user_id)

                if user is None:
                    raise ValueError("User does not exist")

                conversation = Conversation(
                    user_id=user_id,
                    title=title,
                )

                db.add(conversation)
                db.flush()

                conversation_id = conversation.conversation_id

                logger.info(
                    f"Created conversation: {conversation_id}"
                )

                return conversation_id

    # --------------------------------------------------
    # 3. Add a message
    # --------------------------------------------------

    def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
    ):

        if role not in {"user", "assistant"}:
            raise ValueError(
                "Role must be either user or assistant"
            )

        with self.session_factory() as db:
            with db.begin():

                # Lock conversation row to safely allocate
                # message indexes for concurrent requests.
                conversation = db.scalar(
                    select(Conversation)
                    .where(
                        Conversation.conversation_id == conversation_id
                    )
                    .with_for_update()
                )

                if conversation is None:
                    raise ValueError("Conversation does not exist")
                
                if role == "user" and not conversation.title:
                    title = " ".join(content.split())

                    if len(title) > 50:
                        title = title[:47].rstrip() + "..."

                    conversation.title = title
                    
                last_index = db.scalar(
                    select(func.max(Message.message_index))
                    .where(
                        Message.conversation_id == conversation_id
                    )
                )

                next_index = (last_index or 0) + 1

                message = Message(
                    conversation_id=conversation_id,
                    message_index=next_index,
                    role=role,
                    content=content,
                )

                db.add(message)

                conversation.updated_at = datetime.now(timezone.utc)

                logger.info(
                    f"Saved {role} message in {conversation_id}"
                )

        # Invalidate only after PostgreSQL transaction commits
        self._invalidate_history_cache(conversation_id)

    # --------------------------------------------------
    # 4. Get conversation history
    # --------------------------------------------------

    def get_history(self, conversation_id: uuid.UUID):

        cache_key = self._cache_key(conversation_id)

        # First: Try Redis cache
        try:
            cached_history = redis_client.get(cache_key)

            if cached_history is not None:

                logger.info(
                    f"Redis cache HIT for {conversation_id}"
                )

                history_data = json.loads(cached_history)

                return self._convert_to_langchain(history_data)

        except (RedisError, json.JSONDecodeError):
            logger.exception("Redis cache read failed")

        # Second: Cache MISS - fetch from PostgreSQL
        logger.info(
            f"Redis cache MISS for {conversation_id}"
        )

        with self.session_factory() as db:

            messages = db.scalars(
                select(Message)
                .where(
                    Message.conversation_id == conversation_id
                )
                .order_by(Message.message_index.desc())
                .limit(self.HISTORY_LIMIT)
            ).all()

            # Convert newest-first results to chronological order
            messages = list(reversed(messages))

            history_data = [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ]

        # Third: Populate Redis cache
        try:
            redis_client.set(
                cache_key,
                json.dumps(history_data),
                ex=self.CACHE_TTL,
            )

            logger.info(
                f"Cached conversation history: {conversation_id}"
            )

        except RedisError:
            logger.exception("Redis cache write failed")

        return self._convert_to_langchain(history_data)

    # --------------------------------------------------
    # Helper: Convert stored messages to LangChain format
    # --------------------------------------------------

    @staticmethod
    def _convert_to_langchain(history_data):

        chat_history = []

        for message in history_data:

            if message["role"] == "user":
                chat_history.append(
                    HumanMessage(content=message["content"])
                )

            elif message["role"] == "assistant":
                chat_history.append(
                    AIMessage(content=message["content"])
                )

        return chat_history

    # --------------------------------------------------
    # 5. List conversations for a user
    # --------------------------------------------------

    def list_conversations(self, user_id: uuid.UUID):

        with self.session_factory() as db:

            conversations = db.scalars(
                select(Conversation)
                .where(
                    Conversation.user_id == user_id
                )
                .order_by(
                    Conversation.updated_at.desc()
                )
            ).all()

            return [
                {
                    "conversation_id": conversation.conversation_id,
                    "title": conversation.title,
                    "created_at": conversation.created_at,
                    "updated_at": conversation.updated_at,
                }
                for conversation in conversations
            ]

    # --------------------------------------------------
    # 6. Clear conversation history
    # --------------------------------------------------

    def clear_history(self, conversation_id: uuid.UUID):

        with self.session_factory() as db:
            with db.begin():

                conversation = db.get(
                    Conversation,
                    conversation_id,
                )

                if conversation is None:
                    raise ValueError("Conversation does not exist")

                conversation.messages.clear()

                conversation.updated_at = datetime.now(timezone.utc)

                logger.info(
                    f"Cleared conversation: {conversation_id}"
                )

        # Invalidate Redis after successful database commit
        self._invalidate_history_cache(conversation_id)

    def get_messages(self, conversation_id):
        with self.session_factory() as db:
            messages = db.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.message_index.asc())
            ).all()

            return [
                {
                    "message_id": message.message_id,
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at,
                }
                for message in messages
            ]