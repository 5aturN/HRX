"""Роут отчётов, журналов, пользователей и заказов."""
import datetime as dt
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import io
from app.core.db import get_session
from app.models.tables import AuditLog, Customer, Folder, Item, Order, OrderItem, StockMove, User, UserRole
from app.routers.deps import current_user, need_roles
from app.services.reports import MTYPE_RU, build_excel

log = logging.getLogger("hrx.routers.admin")
router = APIRouter(prefix="/api", tags=["отчёты"])

@router.get("/moves")
async def moves(date_from: str | None = None, date_to: str | None = None, mtype: str | None = None,
                session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Движения с фильтрами (дата, тип). Русские названия типов."""
    rows = (await session.execute(select(StockMove, Item).join(Item, Item.id == StockMove.item_id).order_by(StockMove.id.desc()).limit(1000))).all()
    df = dt.date.fromisoformat(date_from) if date_from else None
    dto = dt.date.fromisoformat(date_to) if date_to else None
    out = []
    for m, it in rows:
        day = m.created_at.date() if m.created_at else None
        if df and day and day < df:
            continue
        if dto and day and day > dto:
            continue
        if mtype and m.mtype != mtype:
            continue
        out.append({"id": m.id, "date": m.created_at.isoformat() if m.created_at else None,
                    "mtype": m.mtype, "mtype_ru": MTYPE_RU.get(m.mtype, m.mtype),
                    "sku": it.sku, "name": it.name, "qty": m.qty, "reason": m.reason, "order_id": m.order_id})
    return out

@router.get("/audit")
async def audit(session: AsyncSession = Depends(get_session), user=Depends(current_user), _=Depends(need_roles("admin"))):
    """Журнал действий (только админ)."""
    rows = (await session.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(1000))).scalars().all()
    return [{"id": a.id, "date": a.created_at.isoformat() if a.created_at else None,
             "user_id": a.user_id, "action": a.action, "details": a.details} for a in rows]

@router.get("/report/excel")
async def excel(date_from: str | None = None, date_to: str | None = None,
                session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Скачать Excel: Остатки + Движения за период."""
    df = dt.date.fromisoformat(date_from) if date_from else None
    dto = dt.date.fromisoformat(date_to) if date_to else None
    data = await build_excel(session, df, dto)
    log.info("Отчёт Excel выдан пользователю %s", user.id)
    return StreamingResponse(io.BytesIO(data), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=sklad.xlsx"})

@router.get("/users", dependencies=[Depends(need_roles("admin"))])
async def users(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Заявки и пользователи (админ видит всех)."""
    rows = (await session.execute(select(User).order_by(User.id))).scalars().all()
    out = []
    for u in rows:
        roles = (await session.execute(select(UserRole.role).where(UserRole.user_id == u.id))).scalars().all()
        out.append({"id": u.id, "tg_id": u.tg_id, "username": u.username, "first_name": u.first_name,
                    "last_name": u.last_name, "position": u.position, "status": u.status, "roles": list(roles)})
    return out

@router.post("/users/{uid}/activate", dependencies=[Depends(need_roles("admin"))])
async def activate(uid: int, body: dict, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Админ проверяет заявку: вписывает ФИО/должность, выдаёт роли, активирует."""
    u = await session.get(User, uid)
    if u is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    for k in ("first_name", "last_name", "position"):
        if body.get(k):
            setattr(u, k, body[k])
    roles = body.get("roles") or ["worker"]
    for r in await session.execute(select(UserRole).where(UserRole.user_id == uid)):
        await session.delete(r.scalar_one())
    for r in roles:
        if r not in ("worker", "purchaser", "admin"):
            raise HTTPException(status_code=400, detail=f"Роль {r} неизвестна")
        session.add(UserRole(user_id=uid, role=r))
    u.status = "active"
    session.add(AuditLog(user_id=user.id, action="user_activate", details=f"tg {u.tg_id}, роли {roles}"))
    await session.commit()
    return {"id": u.id, "status": "active", "roles": roles}

@router.post("/users/{uid}/block", dependencies=[Depends(need_roles("admin"))])
async def block(uid: int, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Заблокировать доступ."""
    u = await session.get(User, uid)
    if u is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    u.status = "blocked"
    session.add(AuditLog(user_id=user.id, action="user_block", details=f"tg {u.tg_id}"))
    await session.commit()
    return {"id": u.id, "status": "blocked"}

@router.get("/orders")
async def orders(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Заказы с прогрессом. Первый пункт меню фронта — сборка просто на склад."""
    rows = (await session.execute(select(Order).order_by(Order.id.desc()))).scalars().all()
    out = []
    for o in rows:
        cust = await session.get(Customer, o.customer_id)
        lines = (await session.execute(select(OrderItem, Item).join(Item, Item.id == OrderItem.product_id).where(OrderItem.order_id == o.id))).all()
        items = [{"product": it.sku + " " + it.name, "need": oi.need_qty, "done": oi.done_qty} for oi, it in lines]
        out.append({"id": o.id, "customer": cust.name if cust else "?", "status": o.status, "note": o.note, "items": items})
    return out

@router.post("/orders", dependencies=[Depends(need_roles("worker"))])
async def add_order(body: dict, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Создать заказ может любой (права делим позже)."""
    cname = (body.get("customer") or "").strip()
    if not cname:
        raise HTTPException(status_code=400, detail="Укажите покупателя")
    cust = (await session.execute(select(Customer).where(Customer.name == cname))).scalar_one_or_none()
    if cust is None:
        cust = Customer(name=cname, contact=body.get("contact"))
        session.add(cust)
        await session.flush()
    o = Order(customer_id=cust.id, status="new", note=body.get("note"), created_by=user.id)
    session.add(o)
    await session.flush()
    for line in body.get("items") or []:
        prod = await session.get(Item, line.get("product_id"))
        if prod is None or prod.kind not in ("product", "subassembly"):
            raise HTTPException(status_code=400, detail="В заказ можно только изделия")
        session.add(OrderItem(order_id=o.id, product_id=prod.id, need_qty=int(line.get("need", 1))))
    session.add(AuditLog(user_id=user.id, action="order_add", details=f"Заказ №{o.id}: {cname}"))
    await session.commit()
    return {"id": o.id}


@router.post("/orders/{oid}/status", dependencies=[Depends(need_roles("worker"))])
async def order_status(oid: int, body: dict, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Статус заказа: new → work → done → shipped."""
    o = await session.get(Order, oid)
    if o is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    st = (body.get("status") or "").strip()
    if st not in ("new", "work", "done", "shipped"):
        raise HTTPException(status_code=400, detail="Статус: new, work, done, shipped")
    o.status = st
    session.add(AuditLog(user_id=user.id, action="order_status", details=f"Заказ №{oid} → {st}"))
    await session.commit()
    return {"id": o.id, "status": st}
