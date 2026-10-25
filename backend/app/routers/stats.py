"""Статистика для главной: всего позиций, штук, ниже порога."""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.models.tables import Item
from app.routers.deps import current_user

log = logging.getLogger("hrx.stats")
router = APIRouter(prefix="/api", tags=["статистика"])

@router.get("/stats")
async def stats(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Цифры для главной: позиции, штуки, нехватка."""
    items = (await session.execute(select(Item))).scalars().all()
    total_items = len(items)
    total_qty = sum(i.qty for i in items)
    low = [i for i in items if i.notify_enabled and i.qty <= i.threshold]
    return {"total_items": total_items, "total_qty": total_qty, "low_count": len(low),
            "low": [{"sku": i.sku, "name": i.name, "qty": i.qty} for i in low[:10]]}
