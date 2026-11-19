import sqlite3
from pathlib import Path


class TelemetryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_id TEXT,
                    retrieval_latency_ms REAL,
                    rerank_latency_ms REAL,
                    generation_latency_ms REAL,
                    total_latency_ms REAL,
                    retrieved_candidates INTEGER,
                    compressed_documents INTEGER,
                    final_context_documents INTEGER
                )
            """)

    def record(self, data: dict) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """INSERT INTO telemetry(user_id, session_id, retrieval_latency_ms, rerank_latency_ms,
                   generation_latency_ms, total_latency_ms, retrieved_candidates, compressed_documents,
                   final_context_documents) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["user_id"], data["session_id"], data["retrieval_latency_ms"],
                    data["rerank_latency_ms"], data["generation_latency_ms"], data["total_latency_ms"],
                    data["retrieved_candidates"], data["compressed_documents"],
                    data["final_context_documents"],
                ),
            )

    def summary(self) -> dict:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                """SELECT COUNT(*), COALESCE(AVG(retrieval_latency_ms),0),
                   COALESCE(AVG(rerank_latency_ms),0), COALESCE(AVG(generation_latency_ms),0),
                   COALESCE(AVG(total_latency_ms),0),
                   COALESCE(MAX(retrieved_candidates),0),
                   COALESCE(MAX(compressed_documents),0),
                   COALESCE(MAX(final_context_documents),0)
                   FROM telemetry"""
            ).fetchone()
        return {
            "conversation_count": row[0],
            "retrieval_latency_ms": round(row[1], 3),
            "rerank_latency_ms": round(row[2], 3),
            "generation_latency_ms": round(row[3], 3),
            "total_latency_ms": round(row[4], 3),
            "retrieved_candidates": row[5],
            "compressed_documents": row[6],
            "final_context_documents": row[7],
        }
