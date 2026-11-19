from unittest.mock import patch
from app.compression.reranker import CohereReranker, Reranker


def test_local_reranker_top_k():
    reranker = Reranker("local", threshold=0.0)
    documents = [{"id": str(i), "text": "merge sort python" if i == 0 else "other"} for i in range(7)]
    result, latency = reranker.rerank("merge sort python", documents)
    assert len(result) <= 5
    assert latency >= 0
    assert all(d["rerank_provider"] == "local" for d in result)


def test_cohere_mock():
    reranker = CohereReranker("test-key")
    response = type("Response", (), {
        "results": [type("Result", (), {"index": 0, "relevance_score": 0.9})()]
    })
    with patch("cohere.ClientV2") as client:
        client.return_value.rerank.return_value = response
        result = reranker.rerank("query", [{"id": "1", "text": "answer"}], top_k=5)
    assert result[0]["rerank_provider"] == "cohere"
