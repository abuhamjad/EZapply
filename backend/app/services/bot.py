from sqlalchemy.orm import Session

from app.models import BotState
from app.schemas.api import BotConfig


def get_or_create_state(db: Session) -> BotState:
    state = db.query(BotState).filter(BotState.id == 1).first()
    if state is None:
        state = BotState(id=1)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def set_status(db: Session, status: str) -> BotState:
    state = get_or_create_state(db)
    state.status = status
    db.commit()
    db.refresh(state)
    return state


def update_config(db: Session, config: BotConfig) -> BotState:
    state = get_or_create_state(db)
    for field, value in config.model_dump().items():
        setattr(state, field, value)
    db.commit()
    db.refresh(state)
    return state
