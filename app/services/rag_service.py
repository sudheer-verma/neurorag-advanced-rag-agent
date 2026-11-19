import time
from app.compression.reranker import Reranker
from app.compression.context_compressor import compress_context
from app.memory.fact_extractor import extract_facts
from app.services.llm_service import LLMService


class RAGService:
    def __init__(self, hybrid, memory, persona, reranker, llm):
        self.hybrid = hybrid
        self.memory = memory
        self.persona = persona
        self.reranker = reranker
        self.llm = llm

    def query(self, query: str, user_id: str, session_id: str):
        total_start = time.perf_counter()
        retrieval_start = time.perf_counter()
        candidates = self.hybrid.search(query, top_k=20)
        retrieval_latency = (time.perf_counter() - retrieval_start) * 1000

        reranked, rerank_latency = self.reranker.rerank(query, candidates)
        compressed = compress_context(reranked)

        memories = self.memory.get(user_id)
        persona = self.persona.build_persona(memories)
        answer, generation_latency = self.llm.generate(query, compressed, persona)

        for fact in extract_facts(query):
            self.memory.add(user_id, fact["fact"], fact["category"], session_id)

        total_latency = (time.perf_counter() - total_start) * 1000
        return {
            "answer": answer,
            "sources": [
                {
                    "id": doc["id"],
                    "title": doc.get("title", "Document"),
                    "text": doc.get("text", "")[:500],
                    "rerank_score": doc.get("rerank_score"),
                    "rerank_provider": doc.get("rerank_provider"),
                }
                for doc in compressed
            ],
            "memories_used": memories,
            "telemetry": {
                "retrieval_latency_ms": round(max(retrieval_latency, 0), 3),
                "rerank_latency_ms": round(max(rerank_latency, 0), 3),
                "generation_latency_ms": round(max(generation_latency, 0), 3),
                "total_latency_ms": round(max(total_latency, 0), 3),
                "retrieved_candidates": len(candidates),
                "compressed_documents": len(reranked),
                "final_context_documents": len(compressed),
            },
        }
