"""Фото позиций и аватары: загрузка, ресайз, отдача."""
import io
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.db import get_session
from app.models.tables import AuditLog, Item, User
from app.routers.deps import current_user, need_roles

log = logging.getLogger("hrx.photos")
router = APIRouter(prefix="/api", tags=["фото"])

def _save_img(data: bytes, dest: Path, size: int = 800) -> None:
    """Жмём картинку до size по длинной стороне, сохраняем как JPEG."""
    img = Image.open(io.BytesIO(data))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((size, size))
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=82)

@router.post("/items/{item_id}/photo", dependencies=[Depends(need_roles("worker"))])
async def item_photo(item_id: int, file: UploadFile = File(...), session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Фото позиции (до 10 МБ). Старое затираем."""
    it = await session.get(Item, item_id)
    if it is None:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл больше 10 МБ")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Пустой файл")
    try:
        dest = Path(settings.UPLOAD_DIR) / "items" / f"{item_id}.jpg"
        _save_img(data, dest)
    except Exception:
        log.exception("Не смог сохранить фото")
        raise HTTPException(status_code=400, detail="Это не картинка")
    it.photo_path = str(dest)
    session.add(AuditLog(user_id=user.id, action="photo", details=f"{it.sku}: фото обновлено"))
    await session.commit()
    log.info("Фото: %s", it.sku)
    return {"ok": True}

@router.get("/items/{item_id}/photo")
async def get_item_photo(item_id: int, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Отдать фото позиции (или 404 — фронт покажет заглушку)."""
    it = await session.get(Item, item_id)
    if it is None:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    if it.photo_path and Path(it.photo_path).exists():
        return FileResponse(it.photo_path, media_type="image/jpeg")
    if it.std_code:
        from app.models.tables import StdCatalog
        std = (await session.execute(select(StdCatalog).where(StdCatalog.std_code == it.std_code))).scalar_one_or_none()
        if std and std.photo_path and Path(std.photo_path).exists():
            return FileResponse(std.photo_path, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Фото нет")

@router.post("/me/avatar")
async def my_avatar(file: UploadFile = File(...), session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Свой аватар (любой активный)."""
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл больше 10 МБ")
    try:
        dest = Path(settings.UPLOAD_DIR) / "avatars" / f"{user.id}.jpg"
        _save_img(data, dest, size=256)
    except Exception:
        raise HTTPException(status_code=400, detail="Это не картинка")
    user.avatar_path = str(dest)
    await session.commit()
    return {"ok": True}

@router.get("/users/{uid}/avatar")
async def user_avatar(uid: int, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Аватар человека (или 404)."""
    u = await session.get(User, uid)
    if u is None or not u.avatar_path or not Path(u.avatar_path).exists():
        raise HTTPException(status_code=404, detail="Аватара нет")
    return FileResponse(u.avatar_path, media_type="image/jpeg")

@router.get("/me")
async def me(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Кто я: профиль, роли, моя статистика за неделю."""
    from sqlalchemy import func, select
    from app.models.tables import StockMove, UserRole
    from datetime import datetime, timedelta
    roles = (await session.execute(select(UserRole.role).where(UserRole.user_id == user.id))).scalars().all()
    week = datetime.now() - timedelta(days=7)
    n = await session.scalar(select(func.count()).select_from(StockMove).where(StockMove.user_id == user.id, StockMove.created_at >= week)) or 0
    return {"id": user.id, "tg_id": user.tg_id, "username": user.username, "first_name": user.first_name,
            "last_name": user.last_name, "position": user.position, "status": user.status,
            "roles": list(roles), "week_moves": n, "has_avatar": bool(user.avatar_path)}
