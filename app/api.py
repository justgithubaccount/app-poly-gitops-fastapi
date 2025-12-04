import json
import traceback
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from opentelemetry import metrics
from opentelemetry.trace import get_current_span
from sqlmodel import Session, select

from app.logger import enrich_context

from .core.db import get_session
from .core.project_memory import ProjectMemory
from .integrations.behavior_manager import BehaviorManager
from .models import ChatHistory, ChatHistoryDB, Project, StoredChatMessage
from .schemas import (
    ChatRequest,
    ChatResponse,
    CreateProjectRequest,
    ProjectInfo,
)
from .services.chat_service import ChatService

api_router = APIRouter(
    prefix="/api/v1",
    tags=["chat"]
)

# In-memory fallback (not used when database is configured)
memory = ProjectMemory()
meter = metrics.get_meter(__name__)
chat_counter = meter.create_counter("chat_requests_total")

def get_chat_service():
    return ChatService()

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

@api_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    log = enrich_context(
        event="chat_api_called",
        endpoint="/chat",
        user_message=req.messages[-1].content if req.messages else None
    )

    log.info("Received standard chat request")
    chat_counter.add(1, {"project_id": "standalone"})
    span = get_current_span()
    trace_id = None
    if span and span.get_span_context().trace_id != 0:
        ctx = span.get_span_context()
        trace_id = format(ctx.trace_id, "032x")

    try:
        reply = await chat_service.get_ai_reply(
            req.messages, req.user_api_key, trace_id=trace_id
        )
        return ChatResponse(reply=reply)

    except Exception as e:
        log.bind(event="chat_api_error", error=str(e)).error("Standard chat request failed")
        traceback.print_exc()
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="...")
        raise HTTPException(status_code=500, detail="AI сервис недоступен")

@api_router.post("/projects", response_model=ProjectInfo)
def create_project(
    req: CreateProjectRequest,
    session: Session = Depends(get_session),
):
    project = Project(name=req.name)
    session.add(project)
    session.commit()
    session.refresh(project)
    enrich_context(
        event="project_created",
        project_id=project.id,
        project_name=project.name
    ).info("New project created")
    return ProjectInfo(id=project.id, name=project.name)

@api_router.get("/projects", response_model=list[ProjectInfo])
def list_projects(session: Session = Depends(get_session)):
    enrich_context(event="project_list_requested").info("Project list requested")
    projects = session.exec(select(Project)).all()
    return [ProjectInfo(id=p.id, name=p.name) for p in projects]

@api_router.post("/projects/{project_id}/chat", response_model=ChatResponse)
async def chat_in_project(
    project_id: str,
    req: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    session: Session = Depends(get_session)
):
    log = enrich_context(
        event="project_chat_called",
        endpoint=f"/projects/{project_id}/chat",
        project_id=project_id,
        user_message=req.messages[-1].content if req.messages else None
    )

    log.info("Chat within project requested")
    chat_counter.add(1, {"project_id": project_id})

    span = get_current_span()
    trace_id = None
    span_id = None
    if span and span.get_span_context().trace_id != 0:
        ctx = span.get_span_context()
        trace_id = format(ctx.trace_id, "032x")
        span_id = format(ctx.span_id, "016x")

    try:
        # Ensure project exists
        project = session.get(Project, project_id)
        if not project:
            raise ValueError(f"Проект {project_id} не найден")

        chat_messages = [
            StoredChatMessage(role=m.role, content=m.content)
            for m in req.messages
        ]
        history_db = ChatHistoryDB(
            project_id=project_id,
            messages=json.dumps([m.model_dump() for m in chat_messages], default=json_serial),
            trace_id=trace_id,
            span_id=span_id,
        )
        session.add(history_db)
        session.commit()

        reply = await chat_service.get_ai_reply(
            req.messages, req.user_api_key, project_id=project_id, trace_id=trace_id
        )
        return ChatResponse(reply=reply)

    except ValueError as e:
        log.bind(event="project_not_found").warning("Project not found")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        log.bind(event="project_chat_error", error=str(e)).error("Project chat failed")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ошибка при обращении к AI")

@api_router.get("/projects/{project_id}/history", response_model=list[ChatHistory])
def get_project_history(
    project_id: str,
    session: Session = Depends(get_session)
):
    log = enrich_context(
        event="project_history_requested",
        project_id=project_id
    )

    log.info("Project history requested")

    try:
        project = session.get(Project, project_id)
        if not project:
            raise ValueError(f"Проект {project_id} не найден")
        histories = session.exec(
            select(ChatHistoryDB).where(ChatHistoryDB.project_id == project_id)
        ).all()
        result = []
        for h in histories:
            messages = [StoredChatMessage(**m) for m in json.loads(h.messages)]
            result.append(
                ChatHistory(
                    id=h.id,
                    project_id=h.project_id,
                    messages=messages,
                    trace_id=h.trace_id,
                    span_id=h.span_id,
                    timestamp=h.timestamp,
                )
            )
        return result
    except ValueError as e:
        log.bind(event="project_history_not_found").warning("Project not found when fetching history")
        raise HTTPException(status_code=404, detail=str(e))


@api_router.get("/behavior/schema", summary="Get current behavior schema")
async def get_behavior_schema(request: Request):
    manager: BehaviorManager | None = getattr(request.app.state, "behavior_manager", None)
    if not manager or not manager.behavior:
        raise HTTPException(status_code=404, detail="Behavior not loaded")
    return manager.behavior.model_dump()
