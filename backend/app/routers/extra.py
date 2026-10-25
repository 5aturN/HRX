"""Последние движения + этикетка для печати."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.models.tables import Item, StockMove
from app.routers.deps import current_user
from app.services.reports import MTYPE_RU

log = logging.getLogger("hrx.extra")
router = APIRouter(prefix="/api", tags=["разное"])

@router.get("/recent")
async def recent(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Что сегодня делали: последние 20 движений всех."""
    rows = (await session.execute(select(StockMove, Item).join(Item, Item.id == StockMove.item_id).order_by(StockMove.id.desc()).limit(20))).all()
    return [{"sku": it.sku, "name": it.name, "mtype_ru": MTYPE_RU.get(m.mtype, m.mtype), "qty": m.qty,
             "date": m.created_at.isoformat() if m.created_at else None} for m, it in rows]

@router.get("/items/{item_id}/label", response_class=HTMLResponse)
async def label(item_id: int, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Этикетка для печати: артикул + название + кол-во. Задел под QR."""
    it = await session.get(Item, item_id)
    if it is None:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    return f"<html><head><meta charset=utf-8><title>{it.sku}</title></head><body style=\"font-family:sans-serif;text-align:center\"><h1>{it.sku}</h1><p>{it.name}</p><p>Остаток: {it.qty}</p><p>qr:{it.id}</p></body></html>"
