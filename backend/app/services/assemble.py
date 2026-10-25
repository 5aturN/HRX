"""Сервис сборки: разворачиваем BOM до листьев, используем готовые подсборки, циклы ловим."""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tables import AuditLog, BomChemistry, BomItem, Item, OrderItem, StockMove
from app.schemas.assemble import AssembleCheck, MissingRow

log = logging.getLogger("hrx.assemble")

async def _children(session: AsyncSession, parent_id: int) -> list[BomItem]:
    rows = (await session.execute(select(BomItem).where(BomItem.parent_id == parent_id))).scalars().all()
    return list(rows)

async def _expand(session: AsyncSession, item_id: int, qty: int, seen: set[int]) -> dict[int, int]:
    """Разворачивает состав до листьев (детали/стандарты). Подсборки не трогаем — их считаем отдельно."""
    if item_id in seen:
        raise ValueError("Кольцо в составе: сборка ссылается сама на себя")
    seen = seen | {item_id}
    item = await session.get(Item, item_id)
    if item is None:
        raise ValueError(f"Позиция id={item_id} не найдена")
    if item.kind in ("detail", "standard"):
        return {item_id: qty}
    out: dict[int, int] = {}
    for row in await _children(session, item_id):
        sub = await _expand(session, row.child_id, row.qty * qty, seen)
        for k, v in sub.items():
            out[k] = out.get(k, 0) + v
    chem = (await session.execute(select(BomChemistry).where(BomChemistry.parent_id == item_id))).scalars().all()
    if chem:
        log.info("В составе %s есть химия-пометка (%s шт), в списание не идёт", item.sku, len(chem))
    return out

async def check_assemble(session: AsyncSession, product_id: int, qty: int) -> AssembleCheck:
    """Проверяем: хватает ли готовых подсборок и листьев. Сами ничего не списываем."""
    product = await session.get(Item, product_id)
    if product is None or product.kind not in ("subassembly", "product"):
        raise ValueError("Собирать можно только изделие или подсборку")
    missing: list[MissingRow] = []
    need_subs: list[MissingRow] = []
    for row in await _children(session, product_id):
        child = await session.get(Item, row.child_id)
        need = row.qty * qty
        if child.kind in ("subassembly", "product") and child.qty < need:
            # Готовых не хватает — смотрим, можно ли дособрать
            try:
                leaves = await _expand(session, child.id, need - child.qty, set())
            except ValueError as e:
                raise e
            can_sub = True
            for leaf_id, leaf_need in leaves.items():
                leaf = await session.get(Item, leaf_id)
                if leaf.qty < leaf_need:
                    can_sub = False
                    missing.append(MissingRow(item_id=leaf.id, sku=leaf.sku, name=leaf.name,
                                              need=leaf_need, have=leaf.qty,
                                              build_subassembly_id=child.id, build_subassembly_name=child.name))
            need_subs.append(MissingRow(item_id=child.id, sku=child.sku, name=child.name,
                                        need=need, have=child.qty))
            if not can_sub:
                continue
        elif child.kind in ("detail", "standard"):
            if child.qty < need:
                missing.append(MissingRow(item_id=child.id, sku=child.sku, name=child.name, need=need, have=child.qty))
    # Убираем дубли по листьям (одна деталь в двух подсборках)
    agg: dict[int, MissingRow] = {}
    for m in missing:
        if m.item_id in agg:
            agg[m.item_id].need = max(agg[m.item_id].need, m.need)
        else:
            agg[m.item_id] = m
    missing = list(agg.values())
    return AssembleCheck(can=not missing, missing=missing, need_subassemblies=need_subs)

async def do_assemble(session: AsyncSession, product_id: int, qty: int, order_id: int | None, user_id: int | None) -> dict:
    """Собираем: одна транзакция. Сначала используем готовые подсборки, листья списываем из общей массы."""
    check = await check_assemble(session, product_id, qty)
    if not check.can:
        raise ValueError("Не хватает: " + ", ".join(f"{m.sku} (надо {m.need}, есть {m.have})" for m in check.missing))
    product = await session.get(Item, product_id)
    if order_id is not None:
        from app.models.tables import Order
        order = await session.get(Order, order_id)
        if order is None:
            raise ValueError("Заказ не найден")
        if order.status == "shipped":
            raise ValueError("Заказ уже отгружен")
    # Версия состава = макс. версия строк (история не пересчитывается при правках)
    rows = await _children(session, product_id)
    version = max([r.version for r in rows], default=1)
    for row in rows:
        child = await session.get(Item, row.child_id)
        need = row.qty * qty
        if child.qty < need:
            raise ValueError(f"Пока проверяли, {child.sku} разобрали")
        child.qty -= need
        mtype = "sborka_podsborki" if product.kind == "subassembly" else "sborka"
        if child.kind in ("subassembly", "product"):
            mtype = "sborka"
        session.add(StockMove(item_id=child.id, mtype=mtype, qty=need,
                              reason=f"Сборка {product.sku} x{qty}", order_id=order_id,
                              bom_version=version, user_id=user_id))
    product.qty += qty
    session.add(StockMove(item_id=product.id, mtype="oprihod_podsborki", qty=qty,
                          reason=f"Собрано {product.sku} x{qty}", order_id=order_id,
                          bom_version=version, user_id=user_id))
    if order_id is not None:
        oi = (await session.execute(select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.product_id == product_id))).scalar_one_or_none()
        if oi is not None:
            oi.done_qty += qty
    session.add(AuditLog(user_id=user_id, action="sborka",
                         details=f"{product.sku} x{qty}, заказ {order_id or 'на склад'}, версия состава {version}"))
    await session.commit()
    log.info("Собрано %s x%s (заказ %s)", product.sku, qty, order_id or "на склад")
    # Пороги: что упало ниже — вернём списком, уведомления шлёт отдельный сервис (шаг 3)
    low: list[str] = []
    for row in rows:
        child = await session.get(Item, row.child_id)
        if child.notify_enabled and child.qty <= child.threshold:
            low.append(child.sku)
    return {"product": product.sku, "qty": qty, "bom_version": version, "low": low}
