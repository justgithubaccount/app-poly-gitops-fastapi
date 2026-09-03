# Chat API Microservice

FastAPI микросервис для LLM-чатов с управлением проектами, историей и интеграцией с Notion.

## Возможности

- 🗨️ **Chat API** — standalone и project-scoped чаты
- 📁 **Проекты** — группировка чатов по проектам
- 📜 **История** — сохранение истории с trace_id/span_id
- 🔗 **Notion** — загрузка behavior-схем агентов
- 📊 **Observability** — OpenTelemetry traces/logs/metrics
- 🐳 **Docker** — контейнеризация с uv

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat` | Standalone чат |
| `POST` | `/api/v1/projects` | Создать проект |
| `GET` | `/api/v1/projects` | Список проектов |
| `POST` | `/api/v1/projects/{id}/chat` | Чат в контексте проекта |
| `GET` | `/api/v1/projects/{id}/history` | История чата проекта |
| `GET` | `/api/v1/behavior/schema` | Текущая схема поведения |
| `GET` | `/health` | Health check |

## Запуск

### Локально (с uv)

```bash
# Установить зависимости
uv sync

# Запустить
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build -t chat-api .
docker run -p 8000:8000 --env-file .env chat-api
```

### Docker Compose

```bash
docker compose up --build
```

## Конфигурация

Скопируйте `.env.example` в `.env` и настройте:

```bash
cp .env.example .env
```

**Основные переменные:**

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | - |
| `OPENROUTER_MODEL` | LLM модель | `anthropic/claude-opus-4` |
| `DATABASE_URL` | URL базы данных | `sqlite:///db.sqlite3` |
| `NOTION_TOKEN` | Notion API token (опционально) | - |
| `NOTION_PAGE_ID` | Notion page ID (опционально) | - |
| `OTEL_SERVICE_NAME` | Имя сервиса для трейсинга | `chat-api` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint | `http://localhost:4318` |

## Структура проекта

```
app/
├── main.py              # FastAPI app factory
├── api.py               # API routes (/api/v1)
├── logger.py            # Structured logging (structlog)
├── core/
│   ├── config.py        # Pydantic Settings
│   ├── db.py            # SQLModel database
│   ├── health.py        # Health endpoint
│   ├── llm_client.py    # OpenRouter client
│   └── project_memory.py
├── models/              # SQLModel & Pydantic models
├── schemas/             # API request/response schemas
├── services/            # Business logic (ChatService)
├── integrations/        # Notion, BehaviorManager
├── behavior/            # Agent behavior definitions
└── observability/       # OpenTelemetry setup
```

## Связанные репозитории

- **[app-crewai-cluster](https://github.com/justgithubaccount/app-crewai-cluster)** — CrewAI агенты для инфраструктуры
- **[app-poly-gitops-helm](https://github.com/justgithubaccount/app-poly-gitops-helm)** — Helm-чарт этого сервиса
- **[app-poly-gitops-k8s](https://github.com/justgithubaccount/app-poly-gitops-k8s)** — ArgoCD-манифесты и GitOps
- **[app-mono-gitops](https://github.com/justgithubaccount/app-mono-gitops)** — монорепа, из которой выделен сервис (архив)

## Разработка

```bash
# Тесты
uv run pytest tests/ -v

# Линтер
uv run ruff check app/ tests/

# Type checker
uv run mypy app/

# Все проверки
uv run ruff check app/ tests/ --fix && uv run mypy app/ --ignore-missing-imports && uv run pytest tests/ -v
```

## CI/CD

GitHub Actions (`.github/workflows/`):
- **test.yaml** — pytest, mypy, ruff на PR
- **release.yaml** — semantic release

## Tech Stack

- **Python** 3.11+
- **FastAPI** 0.116+
- **SQLModel** (SQLAlchemy + Pydantic)
- **OpenTelemetry** (traces, logs, metrics)
- **OpenRouter** (LLM provider)
- **uv** (package manager)

## License

MIT
