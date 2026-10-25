"""Асинхронное подключение к БД: SQLite (WAL) локально, PostgreSQL в проде."""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


def _engine_kwargs() -> dict:
    if settings.is_sqlite:
        return {"echo": False, "connect_args": {"check_same_thread": False}}
    # PostgreSQL через asyncpg: пул под многопоточный uvicorn, таймаут — настройками сервера.
    return {
        "echo": False,
        "pool_size": 10,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "connect_args": {"server_settings": {"statement_timeout": "15000"}},
    }


engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs())


if settings.is_sqlite:

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, conn_record) -> None:
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA foreign_keys=ON;")
        cur.execute("PRAGMA busy_timeout=5000;")
        cur.close()
# PostgreSQL: таймаут только через connect_args server_settings (см. _engine_kwargs) —
# синхронный хук connect с cursor() несовместим с asyncpg, поэтому его здесь нет.


SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as s:
        yield s


async def check_db() -> None:
    """Проверка живости БД для /api/health и /api/ready."""
    async with SessionLocal() as s:
        await s.execute(text("SELECT 1"))


async def dispose_engine() -> None:
    await engine.dispose()
