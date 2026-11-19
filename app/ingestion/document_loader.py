from pathlib import Path
from pypdf import PdfReader


def load_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def load_document(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".txt":
        return load_txt(path)
    if suffix == ".pdf":
        return load_pdf(path)
    raise ValueError("Only PDF and TXT files are supported")
