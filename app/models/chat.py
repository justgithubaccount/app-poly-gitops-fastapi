from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

# Импортируем Role из schemas, избегаем дублирования
from ..schemas.chat import Role


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(UTC)


class StoredChatMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role: Role
    content: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=utc_now)


class ChatHistory(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str = Field(..., examples=["proj-123"])
    messages: list[StoredChatMessage]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=utc_now)
