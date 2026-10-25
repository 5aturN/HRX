"""Alembic env (шаг 1, async). Миграции пишем с шага 2; пока БД создаётся create_db.py."""
import asyncio
from alembic import context
from app.core.db import engine, Base
import app.models  # noqa: F401

def run() -> None:
    async def _run() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_run())

run()
