from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.api import BotConfig, BotStateOut, BotStatusUpdate
from app.services import bot

router = APIRouter(prefix="/bot", tags=["bot"])


@router.get("", response_model=BotStateOut)
def get_state(db: Session = Depends(get_db)):
    return bot.get_or_create_state(db)


@router.put("/status", response_model=BotStateOut)
def update_status(payload: BotStatusUpdate, db: Session = Depends(get_db)):
    return bot.set_status(db, payload.status)


@router.put("/config", response_model=BotStateOut)
def update_config(payload: BotConfig, db: Session = Depends(get_db)):
    return bot.update_config(db, payload)
