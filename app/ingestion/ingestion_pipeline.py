from typing import Dict
from app.ingestion.text_splitter import split_parents_and_children
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.sparse_retriever import SparseRetriever
from app.core.logging import configure_logging


class IngestionPipeline:
    def __init__(self, dense: DenseRetriever, sparse: SparseRetriever):
        self.dense = dense
        self.sparse = sparse
        self.parents: Dict[str, dict] = {}
        self.mapping: Dict[str, str] = {}
        self.children: list[dict] = []
        self.logger = configure_logging()

    def ingest(self, text: str, title: str = "Untitled", metadata: dict | None = None) -> dict:
        metadata = metadata or {}
        split = split_parents_and_children(text, title)
        children = []
        for child in split["children"]:
            item = dict(child)
            item.update(metadata)
            item["title"] = title
            item["parent_text"] = next(
                (parent["text"] for parent in split["parents"] if parent["id"] == child["parent_id"]),
                child["text"],
            )
            children.append(item)
        for parent in split["parents"]:
            item = dict(parent)
            item.update(metadata)
            item["title"] = title
            self.parents[parent["id"]] = item
        self.mapping.update(split["mapping"])
        self.children.extend(children)
        dense_count = self.dense.index(children)
        self.sparse.index_documents(self.children)
        self.logger.info("Ingested document %s with %d parents and %d children", title, len(split["parents"]), len(children))
        return {
            "document_id": split["document_id"],
            "title": title,
            "status": "indexed",
            "parent_count": len(split["parents"]),
            "chunk_count": len(children),
            "dense_count": dense_count,
        }

    def delete_document(self, document_id: str) -> int:
        remaining = [child for child in self.children if child.get("document_id") != document_id]
        removed = len(self.children) - len(remaining)
        parent_ids = {
            child.get("parent_id")
            for child in self.children
            if child.get("document_id") == document_id
        }
        self.children = remaining
        for parent_id in parent_ids:
            self.parents.pop(parent_id, None)
        self.mapping = {
            child_id: parent_id
            for child_id, parent_id in self.mapping.items()
            if parent_id not in parent_ids
        }
        dense_count = self.dense.delete_document(document_id)
        self.sparse.index_documents(self.children)
        return max(removed, dense_count)
