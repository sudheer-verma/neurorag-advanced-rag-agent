from fastapi.testclient import TestClient
from app.main import app


def test_two_session_persona_workflow():
    with TestClient(app) as client:
        first = client.post("/api/chat", json={
            "query": "Hello! I work in Python and prefer brief, code-only responses.",
            "user_id": "usr_99",
            "session_id": "session_001",
        })
        assert first.status_code == 200
        second = client.post("/api/chat", json={
            "query": "Write a quick merge sort routine.",
            "user_id": "usr_99",
            "session_id": "session_002",
        })
        assert second.status_code == 200
        answer = second.json()["answer"]
        assert "```python" in answer
        assert "def merge_sort" in answer
