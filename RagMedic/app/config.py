from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "medical_knowledge_v3"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "llama3"
    JWT_SECRET: str = "change_this_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"


settings = Settings()