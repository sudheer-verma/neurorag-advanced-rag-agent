from typing import Dict, Iterable, List


class ParentDocumentRetriever:
    def __init__(self, parents: Dict[str, dict] | None = None, mapping: Dict[str, str] | None = None):
        self.parents = parents or {}
        self.mapping = mapping or {}

    def retrieve(self, child_documents: Iterable[dict]) -> List[dict]:
        results = []
        seen = set()
        for child in child_documents:
            child_id = child.get("id")
            parent_id = child.get("parent_id") or self.mapping.get(child_id)
            parent = self.parents.get(parent_id) if parent_id else None
            if parent is None:
                continue
            if parent["id"] not in seen:
                seen.add(parent["id"])
                results.append(dict(parent))
        return results
