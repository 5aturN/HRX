"""Роут движений, проектов, порогов."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.models.tables import AuditLog, Folder, Item
from app.routers.deps import current_user, need_roles
from app.schemas.moves import MoveDo, ThresholdDo
from app.services.moves import chem_out, scrap, to_project, unscrap

router = APIRouter(prefix="/api", tags=["движения"])

@router.post("/scrap", dependencies=[Depends(need_roles("worker"))])
async def to_scrap(data: MoveDo, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Списать в брак (причина обязательна)."""
    try:
        it = await scrap(session, data.item_id, data.qty, data.reason, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"sku": it.sku, "qty": it.qty}

@router.post("/unscrap", dependencies=[Depends(need_roles("worker"))])
async def to_unscrap(data: MoveDo, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Вернуть на склад."""
    try:
        it = await unscrap(session, data.item_id, data.qty, data.reason, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"sku": it.sku, "qty": it.qty}

@router.get("/projects")
async def projects(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Папки R&D проектов."""
    rows = (await session.execute(select(Folder).where(Folder.ftype == "rnd_project").order_by(Folder.name))).scalars().all()
    return [{"id": f.id, "name": f.name} for f in rows]

@router.post("/projects", dependencies=[Depends(need_roles("admin"))])
async def add_project(body: dict, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Создать папку проекта (только админ)."""
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Название проекта нужно")
    rnd = (await session.execute(select(Folder).where(Folder.ftype == "rnd"))).scalars().first()
    if rnd is None:
        raise HTTPException(status_code=400, detail="Нет корневой папки R&D")
    f = Folder(name=name, parent_id=rnd.id, ftype="rnd_project")
    session.add(f)
    session.add(AuditLog(user_id=user.id, action="project_add", details=name))
    await session.commit()
    return {"id": f.id, "name": name}

@router.post("/to-project", dependencies=[Depends(need_roles("worker"))])
async def issue(data: MoveDo, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Выдать в проект."""
    if not data.project_folder_id:
        raise HTTPException(status_code=400, detail="Выберите проект")
    try:
        it = await to_project(session, data.item_id, data.qty, data.project_folder_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"sku": it.sku, "qty": it.qty}

@router.post("/chem-out", dependencies=[Depends(need_roles("worker"))])
async def chem(data: MoveDo, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Списать химию (тюбик выброшен)."""
    try:
        it = await chem_out(session, data.item_id, data.qty, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"sku": it.sku, "qty": it.qty}

@router.post("/items/{item_id}/threshold", dependencies=[Depends(need_roles("admin"))])
async def threshold(item_id: int, data: ThresholdDo, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Порог и галочка напоминать (только админ)."""
    it = await session.get(Item, item_id)
    if it is None:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    it.threshold = data.threshold
    it.notify_enabled = data.notify_enabled
    session.add(AuditLog(user_id=user.id, action="porog", details=f"{it.sku}: порог {data.threshold}, напоминать={data.notify_enabled}"))
    await session.commit()
    return {"sku": it.sku, "threshold": it.threshold}
