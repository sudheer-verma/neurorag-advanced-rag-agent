from pydantic import BaseModel, Field
from typing import List


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10000)
    user_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)


class TelemetryResponse(BaseModel):
    retrieval_latency_ms: float
    rerank_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float
    retrieved_candidates: int = 0
    compressed_documents: int = 0
    final_context_documents: int = 0


class ChatResponse(BaseModel):
    answer: str
    user_id: str
    session_id: str
    sources: List[dict] = []
    memories_used: List[dict] = []
    telemetry: TelemetryResponse
