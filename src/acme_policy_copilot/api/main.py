import uuid
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from ..pipeline.rag_pipeline import RAGPipeline
from ..conversation.conversation_manager import ConversationManager
from .schemas import ChatRequest, ChatResponse, MessageResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ..auth.router import router as auth_router
from ..database.models import User
from ..auth.dependencies import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.rag_pipeline = RAGPipeline()
    app.state.conversation_manager = ConversationManager()

    yield


app = FastAPI(
    title="Acme Policy Copilot",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/conversations")
def create_conversation(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    manager = request.app.state.conversation_manager

    conversation_id = manager.create_conversation(
        user_id=current_user.user_id
    )

    return {"conversation_id": str(conversation_id)}


@app.get("/conversations")
def list_conversations(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    manager = request.app.state.conversation_manager

    return manager.list_conversations(current_user.user_id)


@app.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_conversation_messages(
    conversation_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    manager = request.app.state.conversation_manager

    conversations = manager.list_conversations(current_user.user_id)

    owned_ids = {c["conversation_id"] for c in conversations}

    if conversation_id not in owned_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return manager.get_messages(conversation_id)


@app.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    manager = request.app.state.conversation_manager

    conversations = manager.list_conversations(current_user.user_id)
    owned_ids = {c["conversation_id"] for c in conversations}

    if payload.conversation_id not in owned_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")

    pipeline = request.app.state.rag_pipeline

    return pipeline.run(
        query=payload.query,
        conversation_id=payload.conversation_id,
    )


@app.post("/chat/stream")
def chat_stream(
    payload: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    manager = request.app.state.conversation_manager

    conversations = manager.list_conversations(current_user.user_id)
    owned_ids = {c["conversation_id"] for c in conversations}

    if payload.conversation_id not in owned_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")

    pipeline = request.app.state.rag_pipeline

    def event_generator():
        for event in pipeline.run_stream(
            query=payload.query,
            conversation_id=payload.conversation_id,
        ):
            yield (
                f"event: {event['type']}\n"
                f"data: {json.dumps(event['data'])}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
