from fastapi import APIRouter, HTTPException


def create_memory_router(memory) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["memories"])

    @router.get("/users/{user_id}/memories")
    def get_memories(user_id: str):
        return memory.get(user_id)

    @router.delete("/users/{user_id}/memories/{memory_id}")
    def delete_memory(user_id: str, memory_id: int):
        if not memory.delete(memory_id, user_id):
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"deleted": True, "memory_id": memory_id}

    return router
