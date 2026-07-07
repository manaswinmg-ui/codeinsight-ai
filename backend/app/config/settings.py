from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "CodeInsight AI"
    ENV: Literal["development", "production", "testing"] = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkeychangeinproduction"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/codeinsight"
    )

    # AI Configurations
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    AI_PROVIDER: str = "openai"
    AI_MODEL: str = "gpt-4o"
    AI_TEMPERATURE: float = 0.2
    AI_MAX_TOKENS: int = 4096
    AI_TIMEOUT: float = 30.0

    # Modular routing & RAG configs
    OPENAI_DEFAULT_MODEL: str = "gpt-5.4-mini"
    OPENAI_FALLBACK_MODEL: str = "gpt-5.5"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    AI_MAX_CONTEXT_SIZE: int = 8192
    AI_MAX_RETRIEVED_FILES: int = 5
    AI_SIMILARITY_THRESHOLD: float = 0.3
    AI_ESCALATION_CONFIDENCE_THRESHOLD: float = 70.0
    AI_RETRY_COUNT: int = 2

    # JWT / Authentication
    JWT_SECRET_KEY: str = "supersecretkeychangeinproduction"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()
