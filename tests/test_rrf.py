from app.retrieval.rrf import reciprocal_rank_fusion


def test_rrf_scores_and_deduplication():
    a = [{"id": "b", "text": "b"}, {"id": "a", "text": "a"}]
    b = [{"id": "a", "text": "a"}, {"id": "c", "text": "c"}]
    result = reciprocal_rank_fusion([a, b])
    assert [item["id"] for item in result] == ["a", "b", "c"]
