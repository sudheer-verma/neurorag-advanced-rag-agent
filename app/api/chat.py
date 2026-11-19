from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse


def create_chat_router(rag_service, telemetry) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["chat"])

    @router.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest):
        result = rag_service.query(request.query, request.user_id, request.session_id)
        telemetry.record({
            "user_id": request.user_id,
            "session_id": request.session_id,
            **result["telemetry"],
        })
        return ChatResponse(
            answer=result["answer"],
            user_id=request.user_id,
            session_id=request.session_id,
            sources=result["sources"],
            memories_used=result["memories_used"],
            telemetry=result["telemetry"],
        )

    return router
