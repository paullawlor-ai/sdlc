"""Chatbot configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # LLM Configuration
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"
    LLM_MAX_TOKENS: int = 1000
    LLM_TEMPERATURE: float = 0.7
    LLM_TIMEOUT_SECONDS: int = 30

    # Conversation
    MAX_CONVERSATION_TURNS: int = 10
    SYSTEM_PROMPT: str = "You are a helpful assistant."

    # RAG
    RAG_ENABLED: bool = False
    RAG_DOCUMENTS_PATH: str = "./data/docs"
    RAG_TOP_K: int = 3

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
