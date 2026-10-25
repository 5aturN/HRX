"""Сервис приёмки: создаёт поставку, приходует в общую массу, пишет историю и журнал."""
import datetime as dt
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tables import Folder, Item, StockMove, Supply, SupplyItem, AuditLog
from app.schemas.receipt import SupplyCreate

log = logging.getLogger("hrx.receipt")

async def create_supply(session: AsyncSession, data: SupplyCreate, user_id: int | None) -> Supply:
    """Приёмка: шапка + строки. Повтор того же sku = плюс к остатку, дублей не плодим."""
    if data.target == "project" and not data.project_folder_id:
        raise ValueError("Для приёмки в проект укажите папку проекта")
    if data.target == "project":
        folder = await session.get(Folder, data.project_folder_id)
        if folder is None or folder.ftype != "rnd_project":
            raise ValueError("Папка проекта не найдена")
    day = data.supply_date or dt.date.today()
    supply = Supply(
        supplier=data.supplier, upd_no=data.upd_no, invoice_no=data.invoice_no,
        supply_date=dt.datetime.combine(day, dt.time.min),
        target=data.target, project_folder_id=data.project_folder_id, created_by=user_id,
    )
    session.add(supply)
    await session.flush()
    total = 0
    for row in data.items:
        if row.kind == "detail" and not row.decimal:
            raise ValueError(f"У детали {row.sku} нужен децимальный номер")
        folder = await session.get(Folder, row.folder_id)
        if folder is None:
            raise ValueError(f"Папка id={row.folder_id} не найдена")
        item = (await session.execute(select(Item).where(Item.sku == row.sku))).scalar_one_or_none()
        if item is None:
            item = Item(sku=row.sku, name=row.name, decimal=row.decimal, folder_id=row.folder_id,
                        kind=row.kind, qty=0, supplier_article=row.supplier_article)
            session.add(item)
            await session.flush()
            log.info("Новая позиция: %s (%s)", row.sku, row.name)
        elif item.kind != row.kind:
            raise ValueError(f"Артикул {row.sku} уже есть как {item.kind}, а пришёл как {row.kind}")
        item.qty += row.qty
        session.add(SupplyItem(supply_id=supply.id, item_id=item.id, qty=row.qty))
        mtype = "prihod" if data.target == "stock" else "vydacha_rd"
        session.add(StockMove(item_id=item.id, mtype=mtype, qty=row.qty,
                              reason=f"Поставка №{supply.id} от {data.supplier}",
                              project_folder_id=data.project_folder_id, user_id=user_id))
        total += row.qty
    session.add(AuditLog(user_id=user_id, action="priemka",
                          details=f"Поставка №{supply.id}: {data.supplier}, позиций {len(data.items)}, штук {total}"))
    await session.commit()
    await session.refresh(supply)
    log.info("Приёмка №%s: %s позиций, %s шт", supply.id, len(data.items), total)
    return supply
