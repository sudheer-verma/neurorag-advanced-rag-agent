import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_postman() -> None:
    path = ROOT / "postman" / "neurorag_collection.json"
    collection = json.loads(path.read_text(encoding="utf-8"))
    assert collection["info"]["schema"].endswith("/collection/v2.1.0/collection.json")
    assert len(collection["item"]) >= 6


def validate_env() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in gitignore
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "OPENAI_API_KEY=" in example
    assert "COHERE_API_KEY=" in example


def main() -> int:
    validate_postman()
    validate_env()
    print("Project configuration validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
