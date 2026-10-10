import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
VECTOR_DIR = STORAGE_DIR / "vector_store"
SAMPLE_DOCS_DIR = BASE_DIR / "sample_documents"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Student Academic Support Agent"
    VERSION: str = "1.0.0"
    DEVELOPER_INFO: str = "AI Student Academic Support Agent"
    API_V1_STR: str = "/api"

    # Security & Auth
    SECRET_KEY: str = "academic-support-agent-supersecure-jwt-signing-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/academic_support.db")

    # AI & RAG Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "local_fallback")  # gemini, openai, local_fallback
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")

    # Document Chunking & Retrieval
    CHUNK_SIZE: int = 550
    CHUNK_OVERLAP: int = 80
    RETRIEVAL_TOP_K: int = 4
    CONFIDENCE_THRESHOLD: float = 0.40

    # Paths
    BASE_DIR: Path = BASE_DIR
    STORAGE_DIR: Path = STORAGE_DIR
    UPLOAD_DIR: Path = UPLOAD_DIR
    VECTOR_DIR: Path = VECTOR_DIR
    SAMPLE_DOCS_DIR: Path = SAMPLE_DOCS_DIR

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
