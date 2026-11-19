def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_and_docs(client):
    assert client.get("/").status_code == 200
    assert client.get("/docs").status_code == 200


def test_chat_and_memories(client):
    first = client.post("/api/chat", json={
        "query": "Hello! I work in Python and prefer brief, code-only responses.",
        "user_id": "usr_test_api",
        "session_id": "session_one",
    })
    assert first.status_code == 200
    telemetry = first.json()["telemetry"]
    assert telemetry["retrieval_latency_ms"] >= 0
    assert telemetry["rerank_latency_ms"] >= 0
    assert telemetry["generation_latency_ms"] >= 0
    assert telemetry["total_latency_ms"] >= 0

    memories = client.get("/api/users/usr_test_api/memories")
    assert memories.status_code == 200
    facts = [item["fact"] for item in memories.json()]
    assert any("Python" in fact for fact in facts)
    assert "Response preference: brief" in facts
    assert "Output preference: code-only" in facts


def test_invalid_chat(client):
    response = client.post("/api/chat", json={"query": "", "user_id": "", "session_id": ""})
    assert response.status_code == 422


def test_document_upload_rejects_unsupported_file(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("notes.md", b"# Notes", "text/markdown")},
    )
    assert response.status_code == 400


def test_empty_upload_is_rejected(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 422
