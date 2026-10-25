"""Папки: дерево склада с остатками."""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.models.tables import Folder, Item
from app.routers.deps import current_user

log = logging.getLogger("hrx.folders")
router = APIRouter(prefix="/api", tags=["папки"])

FTYPE_RU = {"root": "Склад", "serial": "Серийная", "serial_product": "Изделие", "consumable": "Расходники", "consumable_type": "Тип", "rnd": "R&D", "rnd_project": "Проект"}

@router.get("/folders/tree")
async def tree(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Всё дерево: папки, кол-во позиций и штук внутри."""
    folders = (await session.execute(select(Folder).order_by(Folder.id))).scalars().all()
    items = (await session.execute(select(Item))).scalars().all()
    by_folder: dict[int, list] = {}
    for it in items:
        by_folder.setdefault(it.folder_id, []).append(it)
    def subtree(fid: int) -> dict:
        f = next(x for x in folders if x.id == fid)
        kids = [x for x in folders if x.parent_id == fid]
        own = by_folder.get(fid, [])
        total_qty = sum(i.qty for i in own)
        node = {"id": f.id, "name": f.name, "ftype": f.ftype, "ftype_ru": FTYPE_RU.get(f.ftype, f.ftype),
                "items": [{"id": i.id, "sku": i.sku, "name": i.name, "qty": i.qty, "has_photo": bool(i.photo_path)} for i in sorted(own, key=lambda x: x.name)],
                "n_items": len(own), "qty": total_qty, "children": []}
        for k in kids:
            ch = subtree(k.id)
            node["children"].append(ch)
            node["n_items"] += ch["n_items"]
            node["qty"] += ch["qty"]
        return node
    roots = [f for f in folders if f.parent_id is None]
    if not roots:
        return []
    return [subtree(r.id) for r in roots]
