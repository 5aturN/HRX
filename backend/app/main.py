"""Точка входа: API склада. Раздаёт frontend/dist с одного URL (требование Mini App)."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.db import check_db, dispose_engine
from .core.limits import RateLimit
from .core.logging_conf import setup_logging
from .routers import admin, assemble, catalog, extra, favorites, folders, moves, photos, receipt, stats

log = setup_logging(level=settings.LOG_LEVEL, log_dir=settings.LOG_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизнь приложения: готовим каталоги, на выходе закрываем пул БД."""
    for path in (settings.upload_path, settings.backup_path, settings.log_path):
        path.mkdir(parents=True, exist_ok=True)
    yield
    await dispose_engine()


app = FastAPI(title="HRXWarehouse", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
app.add_middleware(RateLimit, per_min=settings.RATE_LIMIT_PER_MIN)
app.include_router(receipt.router)
app.include_router(assemble.router)
app.include_router(moves.router)
app.include_router(admin.router)
app.include_router(photos.router)
app.include_router(folders.router)
app.include_router(stats.router)
app.include_router(catalog.router)
app.include_router(favorites.router)
app.include_router(extra.router)

@app.get("/api/health")
async def health():
    """Проверка живости."""
    log.info("Health-check запрошен")
    return {"ok": True, "app": "HRXWarehouse"}

@app.get("/api/ready")
async def ready():
    """Готовность: отвечает только если жива база (для Docker и Caddy)."""
    try:
        await check_db()
    except Exception:
        log.exception("БД недоступна на /api/ready")
        return JSONResponse({"ok": False, "app": "HRXWarehouse"}, status_code=503)
    return {"ok": True, "app": "HRXWarehouse"}

dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if dist.exists():
    app.mount("/", StaticFiles(directory=str(dist), html=True), name="front")
else:
    @app.get("/")
    async def root():
        return {"app": "HRXWarehouse", "front": "не собран (npm run build)"}
