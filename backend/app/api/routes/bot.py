from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.connection import get_db
from app.models.bot import BotConfig
from app.schemas.bot import (
    BotConfigSchema,
    BotStartRequest,
    BotStartResponse,
    BotStateSchema,
    BotStatusResponse,
    BotStatusUpdate,
    ResolveQuestionRequest,
    ScreeningQuestionResponse,
)
from app.services.bot import BotService
from app.services.learning import LearningService

router = APIRouter(prefix="/bot", tags=["Bot"])

# Singleton config ID used in the bot_config table
_BOT_CONFIG_ID = "default"


@router.get("", response_model=BotStateSchema)
async def get_bot_state(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BotConfig).where(BotConfig.id == _BOT_CONFIG_ID))
    row = result.scalar_one_or_none()
    if row is None:
        return BotStateSchema()
    return BotStateSchema(
        status=row.status,
        linkedin=row.linkedin,
        indeed=row.indeed,
        glassdoor=row.glassdoor,
        dice=row.dice,
        job_type=row.job_type,
        location=row.location,
        min_salary=row.min_salary,
        apply_delay=row.apply_delay,
    )


@router.put("/status", response_model=BotStateSchema)
async def update_bot_status(payload: BotStatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BotConfig).where(BotConfig.id == _BOT_CONFIG_ID))
    row = result.scalar_one_or_none()
    if row is None:
        row = BotConfig(id=_BOT_CONFIG_ID)
        db.add(row)
    row.status = payload.status
    await db.commit()
    await db.refresh(row)
    return BotStateSchema(
        status=row.status,
        linkedin=row.linkedin,
        indeed=row.indeed,
        glassdoor=row.glassdoor,
        dice=row.dice,
        job_type=row.job_type,
        location=row.location,
        min_salary=row.min_salary,
        apply_delay=row.apply_delay,
    )


@router.put("/config", response_model=BotStateSchema)
async def update_bot_config(payload: BotConfigSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BotConfig).where(BotConfig.id == _BOT_CONFIG_ID))
    row = result.scalar_one_or_none()
    if row is None:
        row = BotConfig(id=_BOT_CONFIG_ID)
        db.add(row)
    row.linkedin = payload.linkedin
    row.indeed = payload.indeed
    row.glassdoor = payload.glassdoor
    row.dice = payload.dice
    row.job_type = payload.job_type
    row.location = payload.location
    row.min_salary = payload.min_salary
    row.apply_delay = payload.apply_delay
    await db.commit()
    await db.refresh(row)
    return BotStateSchema(
        status=row.status,
        linkedin=row.linkedin,
        indeed=row.indeed,
        glassdoor=row.glassdoor,
        dice=row.dice,
        job_type=row.job_type,
        location=row.location,
        min_salary=row.min_salary,
        apply_delay=row.apply_delay,
    )


@router.post("/start", response_model=BotStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_bot(payload: BotStartRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await BotService(db).start_run(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/status/{run_id}", response_model=BotStatusResponse)
async def get_bot_status(run_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await BotService(db).get_status(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/stop/{run_id}", response_model=BotStatusResponse)
async def stop_bot(run_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await BotService(db).stop_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/resolve-question", response_model=ScreeningQuestionResponse)
async def resolve_question(payload: ResolveQuestionRequest, db: AsyncSession = Depends(get_db)):
    try:
        resolved = await LearningService(db).resolve_question(
            payload.question_id, payload.answer, payload.remember_for_future
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    await BotService(db).resume_run(resolved.bot_run_id)
    return resolved
