
from src.acme_policy_copilot.conversation.conversation_manager import (
    ConversationManager,
)

manager = ConversationManager()

# Create or retrieve a mock user
user_id = manager.get_or_create_user(
    email="rahul@acme.com",
    name="Rahul",
)

print("User ID:", user_id)


# Create a new conversation
conversation_id = manager.create_conversation(
    user_id=user_id,
    title="Leave Policy",
)

print("Conversation ID:", conversation_id)


# Save messages
manager.add_message(
    conversation_id,
    "user",
    "How many leaves do employees get?",
)

manager.add_message(
    conversation_id,
    "assistant",
    "Employees receive annual leave as per company policy.",
)


# Retrieve history
history1 = manager.get_history(conversation_id)

print("\nConversation history:")

for message in history:
    print(type(message).__name__, ":", message.content)


# List conversations
conversations = manager.list_conversations(user_id)

print("\nUser conversations:")

for conversation in conversations:
    print(conversation)
