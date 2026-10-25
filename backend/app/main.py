"""Точка входа FastAPI: скелет шага 0. Раздаёт frontend/dist с одного URL (требование Mini App)."""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .core.logging_conf import setup_logging

log = setup_logging()
app = FastAPI(title="HRXWarehouse")

@app.get("/api/health")
async def health():
    """Проверка живости (рус.)."""
    log.info("Health-check запрошен")
    return {"ok": True, "app": "HRXWarehouse"}

dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if dist.exists():
    app.mount("/", StaticFiles(directory=str(dist), html=True), name="front")
else:
    @app.get("/")
    async def root():
        return {"app": "HRXWarehouse", "front": "не собран (npm run build)"}
