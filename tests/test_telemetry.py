from app.services.telemetry import TelemetryStore


def test_telemetry_summary(tmp_path):
    store = TelemetryStore(str(tmp_path / "telemetry.sqlite"))
    store.record({
        "user_id": "u", "session_id": "s",
        "retrieval_latency_ms": 1.0, "rerank_latency_ms": 2.0,
        "generation_latency_ms": 3.0, "total_latency_ms": 6.0,
        "retrieved_candidates": 4, "compressed_documents": 2,
        "final_context_documents": 2,
    })
    summary = store.summary()
    assert summary["conversation_count"] == 1
    assert summary["total_latency_ms"] == 6.0
