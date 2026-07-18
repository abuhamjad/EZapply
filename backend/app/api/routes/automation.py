import json
from queue import Empty
from typing import Iterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.automation import (
    AutomationEventResponse,
    BotConfigResponse,
    BotConfigUpdateRequest,
    BotResponseRequest,
    BotStatusResponse,
    BotStatusUpdateRequest,
    StartAutomationRequest,
)
from app.services.automation_service import automation_service
from app.services.event_broker import event_broker


router = APIRouter(prefix="/api/automation", tags=["automation"])


def _conflict(error: ValueError) -> HTTPException:
    return HTTPException(status_code=409, detail=str(error))


@router.get("/status", response_model=BotStatusResponse)
def get_bot_status(database: Session = Depends(get_db)) -> dict:
    return automation_service.status(database)


@router.put("/status", response_model=BotStatusResponse)
def update_bot_status(
    request: BotStatusUpdateRequest,
    database: Session = Depends(get_db),
) -> dict:
    try:
        if request.status == "running":
            return automation_service.start(database)
        if request.status == "paused":
            return automation_service.pause(database)
        return automation_service.stop(database)
    except ValueError as error:
        raise _conflict(error) from error


@router.get("/config", response_model=BotConfigResponse)
def get_bot_config(database: Session = Depends(get_db)) -> dict:
    return automation_service.config(database)


@router.put("/config", response_model=BotConfigResponse)
def update_bot_config(
    request: BotConfigUpdateRequest,
    database: Session = Depends(get_db),
) -> dict:
    return automation_service.update_config(database, request.model_dump())


@router.post("/start", response_model=BotStatusResponse)
def start_bot(
    request: StartAutomationRequest,
    database: Session = Depends(get_db),
) -> dict:
    try:
        config = request.config.model_dump() if request.config is not None else None
        return automation_service.start(database, config)
    except ValueError as error:
        raise _conflict(error) from error


@router.post("/pause", response_model=BotStatusResponse)
def pause_bot(database: Session = Depends(get_db)) -> dict:
    try:
        return automation_service.pause(database)
    except ValueError as error:
        raise _conflict(error) from error


@router.post("/resume", response_model=BotStatusResponse)
def resume_bot(database: Session = Depends(get_db)) -> dict:
    try:
        return automation_service.resume(database)
    except ValueError as error:
        raise _conflict(error) from error


@router.post("/stop", response_model=BotStatusResponse)
def stop_bot(database: Session = Depends(get_db)) -> dict:
    try:
        return automation_service.stop(database)
    except ValueError as error:
        raise _conflict(error) from error


@router.post("/respond", response_model=BotStatusResponse)
def respond_to_question(
    request: BotResponseRequest,
    database: Session = Depends(get_db),
) -> dict:
    try:
        return automation_service.submit_response(database, request.answer)
    except ValueError as error:
        raise _conflict(error) from error


@router.get("/events", response_model=list[AutomationEventResponse])
def get_events(
    run_id: int | None = None,
    database: Session = Depends(get_db),
) -> list[dict]:
    return automation_service.event_history(database, run_id)


def _event_stream() -> Iterator[str]:
    subscriber = event_broker.subscribe()
    try:
        while True:
            try:
                event = subscriber.get(timeout=15)
                yield f"data: {json.dumps(event, default=str)}\n\n"
            except Empty:
                yield ": heartbeat\n\n"
    finally:
        event_broker.unsubscribe(subscriber)


@router.get("/events/stream")
def stream_events() -> StreamingResponse:
    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
