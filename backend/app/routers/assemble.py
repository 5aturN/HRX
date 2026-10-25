"""Роут сборки: список, состав, проверка, кнопка собрать."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.models.tables import BomChemistry, BomItem, Item
from app.routers.deps import current_user, need_roles
from app.schemas.assemble import AssembleCheck, AssembleDo
from app.services.assemble import check_assemble, do_assemble

log = logging.getLogger("hrx.routers.assemble")
router = APIRouter(prefix="/api", tags=["сборка"])

@router.get("/products")
async def products(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Изделия и подсборки (что можно собирать)."""
    rows = (await session.execute(select(Item).where(Item.kind.in_(["product", "subassembly"])).order_by(Item.name))).scalars().all()
    return [{"id": i.id, "sku": i.sku, "name": i.name, "kind": i.kind, "qty": i.qty} for i in rows]

@router.get("/products/{pid}/bom")
async def bom(pid: int, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Состав + химия-пометка + хватает ли."""
    item = await session.get(Item, pid)
    if item is None:
        raise HTTPException(status_code=404, detail="Не найдено")
    rows = (await session.execute(select(BomItem).where(BomItem.parent_id == pid))).scalars().all()
    comp = []
    for r in rows:
        c = await session.get(Item, r.child_id)
        comp.append({"id": c.id, "sku": c.sku, "name": c.name, "need": r.qty, "have": c.qty, "ok": c.qty >= r.qty})
    chem = (await session.execute(select(BomChemistry).where(BomChemistry.parent_id == pid))).scalars().all()
    chem_out = []
    for ch in chem:
        chem_item = await session.get(Item, ch.chemical_id)
        chem_out.append({"name": chem_item.name if chem_item else "?", "note": ch.note})
    return {"product": {"sku": item.sku, "name": item.name, "qty": item.qty}, "components": comp, "chemistry": chem_out}

@router.post("/assemble/check", response_model=AssembleCheck)
async def assemble_check(data: AssembleDo, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Проверка: можно ли собрать, чего не хватает, какие подсборки дособрать."""
    try:
        return await check_assemble(session, data.product_id, data.qty)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/assemble", dependencies=[Depends(need_roles("worker"))])
async def assemble(data: AssembleDo, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Собрать. Одна транзакция, при нехватке ничего не списывается."""
    try:
        return await do_assemble(session, data.product_id, data.qty, data.order_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
