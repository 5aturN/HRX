"""Тесты сборки: проверка нехватки, сборка подсборки и изделия, заказ двигается."""
from sqlalchemy import select
from app.models.tables import Folder, Item, BomItem, Order, OrderItem, Customer, User

H = {"X-Telegram-Init-Data": "dev"}

async def _fid(session) -> int:
    f = (await session.execute(select(Folder).where(Folder.name == "Метизы"))).scalar_one()
    return f.id

async def _mk(session, sku, name, kind, folder, qty=20, **kw):
    it = Item(sku=sku, name=name, kind=kind, folder_id=folder, qty=qty, **kw)
    session.add(it)
    await session.flush()
    return {"id": it.id, "sku": sku}

async def _tree(session):
    f = await _fid(session)
    d1 = await _mk(session, "SB-D1", "Деталь 1", "detail", f, decimal="Д.1")
    d2 = await _mk(session, "SB-D2", "Деталь 2", "detail", f, decimal="Д.2")
    v = await _mk(session, "SB-V", "Винт", "standard", f, qty=100)
    sub = await _mk(session, "SB-S1", "Подсборка", "subassembly", f, qty=0)
    prod = await _mk(session, "SB-P", "Изделие", "product", f, qty=0)
    session.add_all([
        BomItem(parent_id=sub["id"], child_id=d1["id"], qty=2, version=1),
        BomItem(parent_id=sub["id"], child_id=v["id"], qty=4, version=1),
        BomItem(parent_id=prod["id"], child_id=sub["id"], qty=1, version=1),
        BomItem(parent_id=prod["id"], child_id=d2["id"], qty=3, version=1),
    ])
    await session.commit()
    return prod, sub, d1, d2, v

async def _qty(session, sku: str) -> int:
    session.expire_all()
    it = (await session.execute(select(Item).where(Item.sku == sku))).scalar_one()
    return it.qty

async def test_check_shows_missing_subassembly(client, session):
    """Проверка видит: готовых подсборок нет, предлагает дособрать."""
    prod, sub, *_ = await _tree(session)
    r = await client.post("/api/assemble/check", json={"product_id": prod["id"], "qty": 1}, headers=H)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["can"] is True  # листья есть — можно дособрать
    assert any(x["sku"] == "SB-S1" for x in body["need_subassemblies"])

async def test_check_fails_without_leaves(client, session):
    """Без листьев проверка честно говорит чего не хватает."""
    prod, sub, d1, d2, v = await _tree(session)
    it = (await session.execute(select(Item).where(Item.sku == "SB-D1"))).scalar_one()
    it.qty = 0
    await session.commit()
    r = await client.post("/api/assemble/check", json={"product_id": sub["id"], "qty": 1}, headers=H)
    assert r.json()["can"] is False
    assert any(m["sku"] == "SB-D1" for m in r.json()["missing"])

async def test_assemble_sub_then_product(client, session):
    """Собираем подсборку отдельной кнопкой, потом изделие. Остатки сходятся."""
    prod, sub, d1, d2, v = await _tree(session)
    r1 = await client.post("/api/assemble", json={"product_id": sub["id"], "qty": 2}, headers=H)
    assert r1.status_code == 200, r1.text
    assert await _qty(session, "SB-S1") == 2
    r2 = await client.post("/api/assemble", json={"product_id": prod["id"], "qty": 1}, headers=H)
    assert r2.status_code == 200, r2.text
    assert await _qty(session, "SB-P") == 1
    assert await _qty(session, "SB-S1") == 1  # одну использовали

async def test_assemble_moves_order_progress(client, session):
    """Сборка в заказ двигает прогресс."""
    prod, sub, d1, d2, v = await _tree(session)
    u = (await session.execute(select(User).where(User.tg_id == 999))).scalar_one()
    uid = u.id
    cust = Customer(name="К")
    session.add(cust)
    await session.flush()
    o = Order(customer_id=cust.id, status="work", created_by=uid)
    session.add(o)
    await session.flush()
    oid = o.id
    session.add(OrderItem(order_id=oid, product_id=sub["id"], need_qty=5))
    await session.commit()
    r = await client.post("/api/assemble", json={"product_id": sub["id"], "qty": 2, "order_id": oid}, headers=H)
    assert r.status_code == 200, r.text
    session.expire_all()
    oi = (await session.execute(select(OrderItem).where(OrderItem.order_id == oid))).scalar_one()
    assert oi.done_qty == 2

async def test_cycle_rejected(client, session):
    """Кольцо в составе ловим, а не уходим в вечный цикл."""
    f = await _fid(session)
    a = await _mk(session, "CY-A", "А", "subassembly", f, qty=0)
    b = await _mk(session, "CY-B", "Б", "subassembly", f, qty=0)
    session.add_all([BomItem(parent_id=a["id"], child_id=b["id"], qty=1), BomItem(parent_id=b["id"], child_id=a["id"], qty=1)])
    await session.commit()
    r = await client.post("/api/assemble/check", json={"product_id": a["id"], "qty": 1}, headers=H)
    assert r.status_code == 400 and "Кольцо" in r.text
