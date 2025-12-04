import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.logger import enrich_context


class Settings(BaseSettings):
    """
    Конфиг всего приложения.
    Все переменные тянутся из .env — легко расширять и объяснять новым людям.
    """
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_api_url: str = "http://localhost:4000"
    chat_model: str = "openai/gpt-4.1"
    project_name: str = "ChatMicroservice"
    notion_token: str = os.getenv("NOTION_TOKEN", "")
    notion_page_id: str = os.getenv("NOTION_PAGE_ID", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    enrich_context(event="config_loaded").info("Settings loaded")
    return settings
