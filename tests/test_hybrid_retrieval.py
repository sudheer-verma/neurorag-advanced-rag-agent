from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.sparse_retriever import SparseRetriever


class DenseStub:
    def search(self, query, top_k=20):
        return [{"id": "child_1", "parent_id": "parent_1", "text": "retrieval augmented generation"}]


def test_hybrid_retrieval_returns_parent():
    sparse = SparseRetriever()
    children = [{"id": "child_1", "parent_id": "parent_1", "text": "retrieval augmented generation"}]
    sparse.index_documents(children)
    hybrid = HybridRetriever(
        DenseStub(),
        sparse,
        parents={"parent_1": {"id": "parent_1", "text": "Full parent document"}},
        mapping={"child_1": "parent_1"},
    )
    result = hybrid.search("retrieval")
    assert result[0]["id"] == "parent_1"
    assert result[0]["text"] == "Full parent document"
