# CLAUDE.md

Этот файл содержит контекст для Claude Code при работе с проектом.

## О проекте

**Chat API Microservice** — FastAPI сервис для LLM-чатов с проектами, историей и Notion интеграцией.

## Команды

```bash
# Запуск сервера
uv run uvicorn app.main:app --reload

# Тесты
OTEL_SDK_DISABLED=true uv run pytest tests/ -v

# Линтер
uv run ruff check app/ tests/ --fix

# Type checker
uv run mypy app/ --ignore-missing-imports

# Все проверки
uv run ruff check app/ tests/ --fix && uv run mypy app/ --ignore-missing-imports && OTEL_SDK_DISABLED=true uv run pytest tests/ -v
```

## Структура

```
app/
├── main.py              # FastAPI app factory с lifespan
├── api.py               # API routes /api/v1
├── logger.py            # Structlog + OpenTelemetry
├── core/
│   ├── config.py        # Pydantic Settings
│   ├── db.py            # SQLModel database
│   ├── health.py        # Health endpoint
│   └── llm_client.py    # OpenRouter client
├── models/              # SQLModel entities
├── schemas/             # API request/response
├── services/            # ChatService
├── integrations/        # Notion, BehaviorManager
├── behavior/            # Behavior models
└── observability/       # OpenTelemetry tracing
```

## Ключевые файлы

- `app/main.py` — точка входа, lifespan context manager
- `app/api.py` — все API endpoints
- `app/core/config.py` — Settings с SettingsConfigDict
- `app/core/llm_client.py` — OpenRouterClient
- `app/services/chat_service.py` — бизнес-логика чатов

## Стек

- Python 3.11+
- FastAPI + Pydantic v2
- SQLModel (SQLAlchemy + Pydantic)
- OpenTelemetry (traces, logs, metrics)
- OpenRouter (LLM)
- uv (package manager)

## Конвенции

- Pydantic v2: `model_config = SettingsConfigDict(...)` вместо `class Config`
- Datetime: `datetime.now(UTC)` вместо `datetime.utcnow()`
- FastAPI: lifespan context manager вместо `@app.on_event`
- Тесты: `OTEL_SDK_DISABLED=true` для отключения трейсинга

## Связанные репозитории

- `app-crewai-cluster` — CrewAI агенты (отдельный сервис)
- `app-release` — Helm charts и GitOps
