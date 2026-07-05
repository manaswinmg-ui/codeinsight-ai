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


settings = Settings()
