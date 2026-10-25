"""Сервис движений: брак, возврат, выдача в R&D, ручное списание химии, пороги и уведомления."""
import logging
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.tables import AuditLog, Folder, Item, StockMove, UserRole

log = logging.getLogger("hrx.moves")

async def _get(session: AsyncSession, item_id: int) -> Item:
    item = await session.get(Item, item_id)
    if item is None:
        raise ValueError("Позиция не найдена")
    return item

async def _low_list(session: AsyncSession, ids: list[int]) -> list[Item]:
    """Позиции ниже порога, о которых ещё не писали (флаг low_notified — защита от спама)."""
    out = []
    for i in ids:
        it = await session.get(Item, i)
        if it and it.notify_enabled and not it.low_notified and it.qty <= it.threshold:
            out.append(it)
    return out

async def notify_low(items: list[Item], session: AsyncSession) -> int:
    """Шлём закупщикам + копия админу, кто упал ниже порога. Возвращаем сколько отправили."""
    if not items:
        return 0
    if not settings.BOT_TOKEN:
        log.info("BOT_TOKEN нет — уведомления пропускаем (текст в логе)")
        for it in items:
            log.info("Ниже порога: %s (%s): остаток %s, порог %s", it.sku, it.name, it.qty, it.threshold)
        return 0
    rows = (await session.execute(select(UserRole.user_id).where(UserRole.role.in_(["purchaser", "admin"])).distinct())).all()
    from app.models.tables import User
    sent = 0
    for (uid,) in rows:
        u = await session.get(User, uid)
        if not u or not u.tg_id or u.tg_id in (1, 2):
            continue
        lines = "\n".join(f"• {it.sku} ({it.name}): остаток {it.qty}, порог {it.threshold}" for it in items)
        text = f"Склад: ниже порога\n{lines}"
        try:
            async with httpx.AsyncClient(timeout=settings.TELEGRAM_NOTIFY_TIMEOUT) as c:
                r = await c.post(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage",
                                 json={"chat_id": u.tg_id, "text": text})
                if r.status_code == 200:
                    sent += 1
        except Exception:
            log.exception("Не смог отправить уведомление tg %s", u.tg_id)
    log.info("Уведомлений отправлено: %s", sent)
    if sent:
        for it in items:
            it.low_notified = True
        await session.commit()
    return sent

async def scrap(session: AsyncSession, item_id: int, qty: int, reason: str | None, user_id: int | None) -> Item:
    """В брак: минус из общей массы, причина обязательна."""
    if not reason:
        raise ValueError("Укажите причину брака")
    it = await _get(session, item_id)
    if it.qty < qty:
        raise ValueError(f"На складе {it.qty}, а в брак просят {qty}")
    it.qty -= qty
    session.add(StockMove(item_id=it.id, mtype="brak", qty=qty, reason=reason, user_id=user_id))
    session.add(AuditLog(user_id=user_id, action="brak", details=f"{it.sku}: в брак {qty}, причина: {reason}"))
    await session.commit()
    log.info("Брак: %s x%s (%s)", it.sku, qty, reason)
    await notify_low(await _low_list(session, [it.id]), session)
    return it

async def unscrap(session: AsyncSession, item_id: int, qty: int, reason: str | None, user_id: int | None) -> Item:
    """Возврат на склад: плюс к остатку."""
    it = await _get(session, item_id)
    it.qty += qty
    session.add(StockMove(item_id=it.id, mtype="vozvrat", qty=qty, reason=reason or "Возврат", user_id=user_id))
    session.add(AuditLog(user_id=user_id, action="vozvrat", details=f"{it.sku}: возврат {qty}"))
    await session.commit()
    log.info("Возврат: %s x%s", it.sku, qty)
    return it

async def to_project(session: AsyncSession, item_id: int, qty: int, project_folder_id: int, user_id: int | None) -> Item:
    """Выдача в R&D: заказные — из пула проекта, стандарты — из общего с меткой проекта."""
    it = await _get(session, item_id)
    folder = await session.get(Folder, project_folder_id)
    if folder is None or folder.ftype != "rnd_project":
        raise ValueError("Проект не найден")
    if it.qty < qty:
        raise ValueError(f"На складе {it.qty}, а просят {qty}")
    it.qty -= qty
    session.add(StockMove(item_id=it.id, mtype="vydacha_rd", qty=qty,
                          reason=f"В проект {folder.name}", project_folder_id=project_folder_id, user_id=user_id))
    session.add(AuditLog(user_id=user_id, action="vydacha_rd", details=f"{it.sku} x{qty} → {folder.name}"))
    await session.commit()
    log.info("Выдача в %s: %s x%s", folder.name, it.sku, qty)
    await notify_low(await _low_list(session, [it.id]), session)
    return it

async def chem_out(session: AsyncSession, item_id: int, qty: int, user_id: int | None) -> Item:
    """Химия: списание тюбика руками при выбрасывании (в сборку не идёт)."""
    it = await _get(session, item_id)
    if it.qty < qty:
        raise ValueError(f"Остаток {it.qty}, списать просят {qty}")
    it.qty -= qty
    session.add(StockMove(item_id=it.id, mtype="brak", qty=qty, reason="Тюбик выброшен", user_id=user_id))
    await session.commit()
    log.info("Химия списана: %s x%s", it.sku, qty)
    await notify_low(await _low_list(session, [it.id]), session)
    return it
