from app.ingestion.text_splitter import split_parents_and_children
from app.retrieval.parent_document import ParentDocumentRetriever


def test_parent_child_mapping():
    split = split_parents_and_children("x " * 600, "Test", parent_size=1000, child_size=200)
    assert split["parents"]
    assert split["children"]
    assert len(split["mapping"]) == len(split["children"])


def test_missing_mapping_is_handled():
    retriever = ParentDocumentRetriever()
    assert retriever.retrieve([{"id": "missing", "text": "missing"}]) == []
