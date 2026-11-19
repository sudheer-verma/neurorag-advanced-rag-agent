from app.ingestion.text_splitter import split_parents_and_children


def test_empty_document():
    assert split_parents_and_children("")["children"] == []


def test_ingestion_splits_chunks():
    split = split_parents_and_children("A " * 1200, "sample")
    assert len(split["parents"]) >= 1
    assert len(split["children"]) >= len(split["parents"])
