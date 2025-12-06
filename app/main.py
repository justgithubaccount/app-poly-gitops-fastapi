from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .core.db import init_db
from .core.health import health_router
from .logger import enrich_context
from .observability.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for startup and shutdown."""
    # Startup: init database
    enrich_context(event="startup_init_db_start").info("Starting database initialization")
    try:
        init_db()
        enrich_context(event="startup_init_db_success").info("Database initialization completed")
    except Exception as e:
        enrich_context(event="startup_init_db_error", error=str(e)).error("Database initialization failed")
        raise

    enrich_context(event="startup").info("Application initialized")

    yield  # Application runs here

    # Shutdown
    enrich_context(event="shutdown").info("Application shutting down")


def create_app() -> FastAPI:
    enrich_context(event="app_creation_start").info("Starting app creation")

    app = FastAPI(
        title="Chat Microservice",
        version="0.1.0",
        lifespan=lifespan,
    )

    enrich_context(event="middleware_setup_start").info("Setting up middleware")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    enrich_context(event="routes_setup_start").info("Setting up routes")

    # Routes
    app.include_router(api_router)
    app.include_router(health_router)

    enrich_context(event="tracing_setup_start").info("Setting up tracing")

    # Tracing
    setup_tracing(app)

    @app.get("/")
    async def root():
        enrich_context(event="root_called").info("Root endpoint accessed")
        return {
            "status": "ok",
            "service": app.title,
            "version": app.version
        }

    enrich_context(event="app_creation_complete").info("App creation completed")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
