from typing import Iterable, List


def compress_context(documents: Iterable[dict], max_chars: int = 6000) -> List[dict]:
    compressed = []
    used = 0
    for document in documents:
        text = document.get("text", "")
        if not text:
            continue
        remaining = max_chars - used
        if remaining <= 0:
            break
        excerpt = text if len(text) <= remaining else text[:remaining]
        item = dict(document)
        item["text"] = excerpt
        compressed.append(item)
        used += len(excerpt)
    return compressed
