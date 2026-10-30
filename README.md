# Chat API

FastAPI service for LLM chat, project-scoped transcripts, and OpenTelemetry
instrumentation. It is the application backend in the `app-poly-gitops`
engineering lab.

## Overview

The service exposes standalone chat and project workflows. Projects and
successful project transcripts are stored through SQLModel. SQLite is the local
default; `DATABASE_URL` can point to PostgreSQL.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service liveness |
| `POST` | `/api/v1/chat` | Standalone chat |
| `POST` | `/api/v1/projects` | Create a project |
| `GET` | `/api/v1/projects` | List projects |
| `POST` | `/api/v1/projects/{id}/chat` | Chat in a project |
| `GET` | `/api/v1/projects/{id}/history` | Read successful project transcripts |
| `GET` | `/api/v1/behavior/schema` | Read the optional loaded behavior schema |

Project history is written only after the model returns successfully and includes
the submitted messages, assistant reply, timestamp, and available trace/span IDs.
Provider failures return HTTP `502` and are not added to project history.

## Getting started

Requirements: Python 3.11+ and [uv](https://docs.astral.sh/uv/).

~~~bash
cp .env.example .env
uv sync --locked --dev
uv run uvicorn app.main:app --reload
~~~

Open `http://127.0.0.1:8000/docs` for the generated API documentation.
Configure `OPENROUTER_API_KEY` for real model requests. The provider URL and
model are controlled by `OPENROUTER_API_URL` and `OPENROUTER_MODEL`.

To run the container instead:

~~~bash
docker build -t chat-api .
docker run --rm -p 8000:8000 --env-file .env chat-api
~~~

## Development

~~~bash
OTEL_SDK_DISABLED=true uv run pytest tests/ -v
uv run ruff check app tests
uv run mypy app --ignore-missing-imports
docker build -t app-poly-gitops-fastapi:test .
bash tests/test_container_runtime.sh app-poly-gitops-fastapi:test
~~~

The CI workflow runs the Python checks and verifies that the built container
starts without external services. Releases from `main` publish versioned images
to GitHub Container Registry.

## Repository structure

- `app/` — API routes, persistence, provider client, and telemetry setup
- `tests/` — unit, contract, observability, and container-runtime tests
- `Dockerfile` and `docker-compose.yml` — container entrypoints
- `Taskfile.yaml` — local development commands

## Related repositories

- [app-poly-gitops-ui](https://github.com/justgithubaccount/app-poly-gitops-ui) — browser client
- [app-poly-gitops-helm](https://github.com/justgithubaccount/app-poly-gitops-helm) — Kubernetes package
- [app-poly-gitops-k8s](https://github.com/justgithubaccount/app-poly-gitops-k8s) — GitOps desired state
- [app-poly-gitops-crewai](https://github.com/justgithubaccount/app-poly-gitops-crewai) — Kubernetes automation service
- [app-mono-gitops](https://github.com/justgithubaccount/app-mono-gitops) — archived predecessor

## License

MIT
