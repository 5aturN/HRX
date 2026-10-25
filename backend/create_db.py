"""Создание БД из моделей (шаг 1). Запуск из папки backend: ../backend/.venv/Scripts/python create_db.py"""
import asyncio
import logging
from app.core.db import Base, engine
import app.models  # noqa: F401 — регистрация таблиц

log = logging.getLogger("hrx.seed")

async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("БД создана: %s", sorted(Base.metadata.tables.keys()))

if __name__ == "__main__":
    asyncio.run(main())
