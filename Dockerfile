FROM python:3.11-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (cache layer)
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev)
RUN uv sync --frozen --no-dev

# Copy application code
COPY ./app ./app

# Expose port
EXPOSE 8000

# Run the environment assembled at build time. Runtime startup must not resolve,
# download, or install dependencies.
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Trigger rebuild
