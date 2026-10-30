# CLAUDE.md

Контекст для Claude Code при работе с проектом.

## О проекте

**Chat API Microservice** — FastAPI сервис для LLM-чатов с проектами, историей и опциональной загрузкой behavior из Notion.

## Команды

```bash
# Запуск сервера
uv run uvicorn app.main:app --reload

# Тесты
OTEL_SDK_DISABLED=true uv run pytest tests/ -v

# Линтер (не изменяет файлы)
uv run ruff check app/ tests/

# Явное применение исправлений Ruff
uv run ruff check app/ tests/ --fix

# Type checker
uv run mypy app/ --ignore-missing-imports

# Все проверки
task check
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
├── models/
│   ├── chat.py          # Chat models
│   └── db_models.py     # SQLModel entities
├── schemas/
│   ├── chat.py          # Chat request/response
│   └── projects.py      # Project schemas
├── services/
│   └── chat_service.py  # ChatService бизнес-логика
├── integrations/
│   ├── notion_client.py # Notion API client
│   └── behavior_manager.py # Behavior loading
├── behavior/
│   └── models.py        # Behavior models
└── observability/
    └── tracing.py       # OpenTelemetry setup
```

## API Endpoints

- `GET /` — status
- `GET /health` — health check
- `POST /api/v1/chat` — standalone chat
- `POST /api/v1/projects` — create project
- `GET /api/v1/projects` — list projects
- `POST /api/v1/projects/{id}/chat` — chat in project
- `GET /api/v1/projects/{id}/history` — chat history
- `GET /api/v1/behavior/schema` — current behavior

## Стек

- Python 3.11+
- FastAPI + Pydantic v2
- SQLModel (SQLAlchemy + Pydantic)
- OpenTelemetry (traces, logs, metrics)
- OpenRouter (LLM)
- uv (package manager)
- structlog (logging)
- httpx (HTTP client)
- httpx + PyYAML (опциональная Notion/behavior интеграция)

## Конвенции

- Pydantic v2: `model_config = SettingsConfigDict(...)` вместо `class Config`
- Datetime: `datetime.now(UTC)` вместо `datetime.utcnow()`
- FastAPI: lifespan context manager вместо `@app.on_event`
- Тесты: `OTEL_SDK_DISABLED=true` для отключения трейсинга
- Логирование: `enrich_context(event="name").info("message")`
- SQLModel — единственное хранилище проектов и истории; in-memory fallback отсутствует
- NotionClient/BehaviorManager — опциональная заготовка, по умолчанию не подключена

## Связанные репозитории

- `app-poly-gitops-k8s` — GitOps манифесты (ArgoCD Applications)
- `app-poly-gitops-helm` — Helm chart для сервисов
- `app-poly-gitops-crewai` — CrewAI мониторинг
