"""Точка входа: API склада. Раздаёт frontend/dist с одного URL (требование Mini App)."""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .core.logging_conf import setup_logging
from .routers import admin, assemble, catalog, folders, moves, photos, receipt, stats

log = setup_logging()
app = FastAPI(title="HRXWarehouse")
app.include_router(receipt.router)
app.include_router(assemble.router)
app.include_router(moves.router)
app.include_router(admin.router)
app.include_router(photos.router)
app.include_router(folders.router)
app.include_router(stats.router)
app.include_router(catalog.router)

@app.get("/api/health")
async def health():
    """Проверка живости."""
    log.info("Health-check запрошен")
    return {"ok": True, "app": "HRXWarehouse"}

dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if dist.exists():
    app.mount("/", StaticFiles(directory=str(dist), html=True), name="front")
else:
    @app.get("/")
    async def root():
        return {"app": "HRXWarehouse", "front": "не собран (npm run build)"}
