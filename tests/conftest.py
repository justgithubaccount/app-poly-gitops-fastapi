import os

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture(scope="session", autouse=True)
def disable_otel():
    """Disable OpenTelemetry for tests."""
    os.environ["OTEL_SDK_DISABLED"] = "true"


@pytest.fixture
def client():
    """Create test client for the app."""
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_openrouter(monkeypatch):
    """Mock OpenRouter API calls."""
    async def mock_generate_reply(*args, **kwargs):
        return "Mocked response from AI"

    monkeypatch.setattr(
        "app.core.llm_client.OpenRouterClient.generate_reply",
        mock_generate_reply
    )
