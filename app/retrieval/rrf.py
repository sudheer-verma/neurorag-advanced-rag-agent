from typing import Iterable, List


def reciprocal_rank_fusion(ranked_lists: Iterable[List[dict]], k: int = 60) -> List[dict]:
    scores = {}
    documents = {}
    for ranked in ranked_lists:
        for rank, document in enumerate(ranked, start=1):
            key = document.get("id") or document.get("parent_id") or document.get("text", "")
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            if key not in documents:
                documents[key] = document
    return [documents[key] for key in sorted(scores, key=lambda item: (-scores[item], str(item)))]
