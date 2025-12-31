from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    API_V1_STR: str = "/v1"

    # Cohere Settings
    COHERE_API_KEY: str
    EMBEDDING_MODEL: str = "embed-english-v3.0"

    # Google Gemini Settings
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-pro"

    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "textbook_content"

    # Database Settings - Using SQLite for local development
    DATABASE_URL: str = "sqlite:///./rag_chatbot.db"
    DATABASE_POOL_SIZE: int = 5  # Smaller pool for SQLite
    DATABASE_POOL_OVERFLOW: int = 0

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]  # In production, specify exact origins

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Embedding Settings
    EMBEDDING_BATCH_SIZE: int = 10
    EMBEDDING_VECTOR_SIZE: int = 1024  # For Cohere embeddings (embed-english-v3.0)

    # Retrieval Settings
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MIN_SCORE: float = 0.5

    # Text Processing
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 51  # 10% of chunk size

    # Session Settings
    SESSION_EXPIRY_HOURS: int = 24

    # Model Settings
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.1

    # API Settings
    API_TIMEOUT: int = 30

    class Config:
        env_file = ".env"


settings = Settings()