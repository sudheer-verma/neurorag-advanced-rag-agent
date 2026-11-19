import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import pipeline
from app.ingestion.document_loader import load_document


def main():
    sample_dir = Path(__file__).resolve().parents[1] / "data" / "sample_documents"
    for path in sorted(sample_dir.glob("*")):
        if path.suffix.lower() in {".txt", ".pdf"}:
            text = load_document(str(path))
            result = pipeline.ingest(text, path.stem, {"filename": path.name})
            print(f"Indexed {path.name}: {result['chunk_count']} chunks")


if __name__ == "__main__":
    main()
