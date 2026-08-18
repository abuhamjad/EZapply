"""
SQLite engine + session factory.
All models inherit from `Base`. `get_db` is the FastAPI dependency
routers/services use to get a session.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a DB session, closes it after the request."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables. Called once on app startup (swap for Alembic in prod)."""
    # Import models so they register on Base.metadata before create_all
    from app.models import application, bot, question, resume, saved_info  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await _reset_stale_runs()


async def _reset_stale_runs() -> None:
    """
    On every server start, mark any non-terminal BotRuns as STOPPED and
    reset BotConfig.status to 'stopped'. This prevents the frontend from
    showing a stuck 'running' or 'login_buffer' state after a server restart.
    """
    from datetime import datetime, timezone
    from sqlalchemy import select
    from app.models.bot import BotConfig, BotRun

    TERMINAL = {"STOPPED", "COMPLETED", "FAILED"}

    async with AsyncSessionLocal() as db:
        runs = (
            await db.execute(select(BotRun).where(BotRun.status.notin_(TERMINAL)))
        ).scalars().all()

        for run in runs:
            run.status = "STOPPED"
            run.finished_at = datetime.now(timezone.utc)
            run.error_message = "Cleared: server restarted while run was active."

        cfg_res = await db.execute(select(BotConfig).where(BotConfig.id == "default"))
        cfg = cfg_res.scalar_one_or_none()
        if cfg:
            cfg.status = "stopped"

        await db.commit()

