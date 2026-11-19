from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    openai_api_key: str = ""
    cohere_api_key: str = ""
    qdrant_url: str = ""
    mem0_api_key: str = ""
    llm_provider: str = "local"
    embedding_provider: str = "local"
    rerank_provider: str = "local"
    memory_provider: str = "local"
    qdrant_path: str = str(ROOT_DIR / "storage" / "qdrant")
    memory_db_path: str = str(ROOT_DIR / "storage" / "memory.sqlite")
    telemetry_db_path: str = str(ROOT_DIR / "storage" / "telemetry.sqlite")
    upload_dir: str = str(ROOT_DIR / "data" / "uploads")
    cors_origins: str = "*"
    rerank_threshold: float = 0.25

    model_config = SettingsConfigDict(env_file=str(ROOT_DIR / ".env"), extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
