"""Избранное: своё у каждого, переключается одной кнопкой."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.models.tables import Favorite, Item
from app.routers.deps import current_user

router = APIRouter(prefix="/api", tags=["избранное"])

@router.get("/favorites")
async def mine(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Моё избранное: позиции с остатками."""
    rows = (await session.execute(select(Favorite, Item).join(Item, Item.id == Favorite.item_id).where(Favorite.user_id == user.id).order_by(Item.name))).all()
    return [{"id": it.id, "sku": it.sku, "name": it.name, "qty": it.qty, "has_photo": bool(it.photo_path or it.std_code)} for _, it in rows]

@router.post("/favorites/{item_id}")
async def toggle(item_id: int, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Звездочка: есть — убрать, нет — добавить."""
    it = await session.get(Item, item_id)
    if it is None:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    old = (await session.execute(select(Favorite).where(Favorite.user_id == user.id, Favorite.item_id == item_id))).scalar_one_or_none()
    if old:
        await session.delete(old)
        await session.commit()
        return {"fav": False}
    session.add(Favorite(user_id=user.id, item_id=item_id))
    await session.commit()
    return {"fav": True}
