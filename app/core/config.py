from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.logger import enrich_context


class Settings(BaseSettings):
    """
    Конфиг приложения. Все переменные из ENV (синхронизировано с Helm values).
    """
    # OpenRouter LLM
    openrouter_api_key: str = ""
    openrouter_api_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_model: str = "anthropic/claude-sonnet-4"

    # Database
    database_url: str = "sqlite:///db.sqlite3"

    # Application
    environment: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    enrich_context(event="config_loaded").info("Settings loaded")
    return settings
