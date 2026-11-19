from typing import Dict, List
from app.utils.helpers import normalize, stable_id


def split_parents_and_children(text: str, title: str = "", parent_size: int = 1000, child_size: int = 200) -> Dict:
    text = normalize(text)
    if not text:
        return {"parents": [], "children": [], "mapping": {}}

    parent_units: List[str] = []
    for start in range(0, len(text), parent_size):
        chunk = text[start:start + parent_size]
        if chunk:
            parent_units.append(chunk)

    parents = []
    children = []
    mapping = {}
    document_id = stable_id(f"{title}:{text}", "doc_")

    for parent_index, parent_text in enumerate(parent_units):
        parent_id = stable_id(f"{document_id}:{parent_index}:{parent_text}", "parent_")
        parents.append({
            "id": parent_id,
            "document_id": document_id,
            "title": title,
            "text": parent_text,
        })
        overlap_start = 0
        while overlap_start < len(parent_text):
            child_text = parent_text[overlap_start:overlap_start + child_size]
            if not child_text:
                break
            child_id = stable_id(f"{parent_id}:{overlap_start}:{child_text}", "child_")
            children.append({
                "id": child_id,
                "parent_id": parent_id,
                "document_id": document_id,
                "title": title,
                "text": child_text,
            })
            mapping[child_id] = parent_id
            overlap_start += child_size

    return {"parents": parents, "children": children, "mapping": mapping, "document_id": document_id}
