"""Configuration tests."""

from app.core.config import Settings, get_settings


def test_settings_defaults():
    """Test Settings has correct defaults."""
    settings = Settings()
    assert settings.openrouter_api_url == "https://openrouter.ai/api/v1/chat/completions"
    assert settings.openrouter_model == "anthropic/claude-sonnet-4"
    assert settings.environment == "development"


def test_get_settings_cached():
    """Test get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_settings_database_url_default():
    """Test default database URL is SQLite."""
    settings = Settings()
    assert "sqlite" in settings.database_url
