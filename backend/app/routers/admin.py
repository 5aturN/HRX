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

def _parse_date(value: str | None, field: str) -> dt.date | None:
    if value is None:
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"{field} должен быть датой в формате ГГГГ-ММ-ДД") from exc


@router.get("/moves")
async def moves(date_from: str | None = None, date_to: str | None = None, mtype: str | None = None,
                session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Движения с фильтрами (дата, тип). Русские названия типов."""
    stmt = select(StockMove, Item).join(Item, Item.id == StockMove.item_id).order_by(StockMove.id.desc())
    df = _parse_date(date_from, "date_from")
    dto = _parse_date(date_to, "date_to")
    if df:
        stmt = stmt.where(StockMove.created_at >= dt.datetime.combine(df, dt.time.min))
    if dto and dto < dt.date.max:
        stmt = stmt.where(StockMove.created_at < dt.datetime.combine(dto + dt.timedelta(days=1), dt.time.min))
    if mtype:
        stmt = stmt.where(StockMove.mtype == mtype)
    rows = (await session.execute(stmt.limit(1000))).all()
    out = []
    for m, it in rows:
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
    df = _parse_date(date_from, "date_from")
    dto = _parse_date(date_to, "date_to")
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
    raw_customer = body.get("customer")
    if not isinstance(raw_customer, str) or not raw_customer.strip():
        raise HTTPException(status_code=400, detail="Укажите покупателя")
    cname = raw_customer.strip()
    raw_lines = body.get("items")
    if raw_lines is None:
        lines = []
    elif not isinstance(raw_lines, list):
        raise HTTPException(status_code=400, detail="Позиции заказа должны быть списком")
    else:
        lines = raw_lines
    order_lines: list[tuple[int, int]] = []
    seen_products: set[int] = set()
    for line in lines:
        if not isinstance(line, dict):
            raise HTTPException(status_code=400, detail="Строка заказа должна быть объектом")
        product_id = line.get("product_id")
        need = line.get("need", 1)
        if isinstance(product_id, bool) or not isinstance(product_id, int):
            raise HTTPException(status_code=400, detail="product_id должен быть целым числом")
        if isinstance(need, bool) or not isinstance(need, int) or need < 1 or need > 100000:
            raise HTTPException(status_code=400, detail="Количество в заказе должно быть целым числом от 1 до 100000")
        if product_id in seen_products:
            raise HTTPException(status_code=400, detail="Изделие нельзя указать в заказе дважды")
        prod = await session.get(Item, product_id)
        if prod is None or prod.kind not in ("product", "subassembly"):
            raise HTTPException(status_code=400, detail="В заказ можно только изделия")
        seen_products.add(product_id)
        order_lines.append((prod.id, need))

    cust = (await session.execute(select(Customer).where(Customer.name == cname))).scalar_one_or_none()
    if cust is None:
        cust = Customer(name=cname, contact=body.get("contact"))
        session.add(cust)
        await session.flush()
    o = Order(customer_id=cust.id, status="new", note=body.get("note"), created_by=user.id)
    session.add(o)
    await session.flush()
    session.add_all([OrderItem(order_id=o.id, product_id=product_id, need_qty=need) for product_id, need in order_lines])
    session.add(AuditLog(user_id=user.id, action="order_add", details=f"Заказ №{o.id}: {cname}"))
    await session.commit()
    return {"id": o.id}


@router.post("/orders/{oid}/status", dependencies=[Depends(need_roles("worker"))])
async def order_status(oid: int, body: dict, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Статус заказа: new → work → done → shipped."""
    o = await session.get(Order, oid)
    if o is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    raw_status = body.get("status")
    if not isinstance(raw_status, str):
        raise HTTPException(status_code=400, detail="Статус должен быть строкой: new, work, done, shipped")
    st = raw_status.strip()
    if st not in ("new", "work", "done", "shipped"):
        raise HTTPException(status_code=400, detail="Статус: new, work, done, shipped")
    o.status = st
    session.add(AuditLog(user_id=user.id, action="order_status", details=f"Заказ №{oid} → {st}"))
    await session.commit()
    return {"id": o.id, "status": st}
