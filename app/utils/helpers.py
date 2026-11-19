import hashlib
import re


def stable_id(text: str, prefix: str = "") -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}{digest}"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
