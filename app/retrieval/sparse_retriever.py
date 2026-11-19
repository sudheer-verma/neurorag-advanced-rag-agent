from rank_bm25 import BM25Okapi
from typing import List


class SparseRetriever:
    def __init__(self):
        self.documents: List[dict] = []
        self.index = None

    def index_documents(self, documents: List[dict]) -> None:
        self.documents = documents
        tokenized = [doc["text"].lower().split() for doc in documents]
        self.index = BM25Okapi(tokenized) if tokenized else None

    def search(self, query: str, top_k: int = 20) -> List[dict]:
        if not self.index:
            return []
        scores = self.index.get_scores(query.lower().split())
        ranked = sorted(zip(scores, self.documents), key=lambda item: (-item[0], item[1]["id"]))
        return [doc for score, doc in ranked[:top_k] if score > 0]
