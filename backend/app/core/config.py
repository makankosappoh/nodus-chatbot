"""
app/core/config.py
------------------
Central config loaded from .env via pydantic-settings.
Every other module imports `settings` from here — never os.getenv() directly.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Groq (active)
    groq_api_key: str = ""

    # PostgreSQL
    database_url: str

    # App
    app_env: str = "development"
    cors_origin: str = "http://localhost:5173"
    log_level: str = "INFO"

    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"

    # RAG tuning
    retriever_k: int = 3
    similarity_threshold: float = 0.3
    chunk_size: int = 400
    chunk_overlap: int = 50

    # Session
    context_window_turns: int = 6

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached so settings object is built only once per process."""
    return Settings()


settings = get_settings()