from app.retrieval.rrf import reciprocal_rank_fusion
from app.retrieval.parent_document import ParentDocumentRetriever


class HybridRetriever:
    def __init__(self, dense, sparse, parents=None, mapping=None):
        self.dense = dense
        self.sparse = sparse
        self.parent = ParentDocumentRetriever(parents, mapping)

    def search(self, query: str, top_k: int = 20):
        dense = self.dense.search(query, top_k=top_k)
        sparse = self.sparse.search(query, top_k=top_k)
        fused_children = reciprocal_rank_fusion([dense, sparse])
        return self.parent.retrieve(fused_children)[:top_k]
