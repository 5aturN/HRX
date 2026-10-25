"""Каталог стандартов: выбрал код — название и фото подтянулись сами."""
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.db import get_session
from app.models.tables import AuditLog, StdCatalog
from app.routers.deps import current_user, need_roles
from app.routers.photos import _save_img

log = logging.getLogger("hrx.catalog")
router = APIRouter(prefix="/api", tags=["каталог"])

@router.get("/catalog")
async def catalog(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Все эталоны: код, название, есть ли фото."""
    rows = (await session.execute(select(StdCatalog).order_by(StdCatalog.std_code))).scalars().all()
    return [{"code": r.std_code, "title": r.title, "descr": r.descr, "has_photo": bool(r.photo_path and Path(r.photo_path).exists())} for r in rows]

@router.post("/catalog", dependencies=[Depends(need_roles("admin"))])
async def add_std(body: dict, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Новый эталон (админ): код + название + описание."""
    code = (body.get("code") or "").strip().upper()
    title = (body.get("title") or "").strip()
    if not code or not title:
        raise HTTPException(status_code=400, detail="Нужны код и название")
    old = (await session.execute(select(StdCatalog).where(StdCatalog.std_code == code))).scalar_one_or_none()
    if old:
        old.title = title; old.descr = body.get("descr")
    else:
        session.add(StdCatalog(std_code=code, title=title, descr=body.get("descr")))
    session.add(AuditLog(user_id=user.id, action="catalog_add", details=f"{code}: {title}"))
    await session.commit()
    return {"code": code}

@router.post("/catalog/{code}/photo", dependencies=[Depends(need_roles("admin"))])
async def std_photo(code: str, file: UploadFile = File(...), session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Фото эталона — одно на всех, кто выбрал этот код."""
    code = code.upper()
    row = (await session.execute(select(StdCatalog).where(StdCatalog.std_code == code))).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Сначала создайте эталон с таким кодом")
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл больше 10 МБ")
    try:
        dest = Path(settings.UPLOAD_DIR) / "catalog" / f"{code}.jpg"
        _save_img(data, dest)
    except Exception:
        raise HTTPException(status_code=400, detail="Это не картинка")
    row.photo_path = str(dest)
    await session.commit()
    log.info("Каталог: фото %s", code)
    return {"ok": True}

@router.get("/catalog/{code}/photo")
async def get_std_photo(code: str, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Фото эталона."""
    row = (await session.execute(select(StdCatalog).where(StdCatalog.std_code == code.upper()))).scalar_one_or_none()
    if row is None or not row.photo_path or not Path(row.photo_path).exists():
        raise HTTPException(status_code=404, detail="Фото нет")
    return FileResponse(row.photo_path, media_type="image/jpeg")
