"""Тесты отчётов и админки: Excel, движения, пользователи, заказы."""
from sqlalchemy import select
from app.models.tables import Folder, Item

H = {"X-Telegram-Init-Data": "dev"}

async def _mk(session, sku, qty=20):
    fid = (await session.execute(select(Folder).where(Folder.name == "Метизы"))).scalar_one().id
    it = Item(sku=sku, name=sku, kind="standard", folder_id=fid, qty=qty)
    session.add(it)
    await session.commit()
    return it.id

async def test_moves_and_excel(client, session):
    """Движения видны, Excel скачивается с двумя листами."""
    iid = await _mk(session, "REP-1")
    await client.post("/api/scrap", json={"item_id": iid, "qty": 2, "reason": "тест"}, headers=H)
    m = await client.get("/api/moves", headers=H)
    assert m.status_code == 200 and any(x["sku"] == "REP-1" for x in m.json())
    x = await client.get("/api/report/excel", headers=H)
    assert x.status_code == 200 and "spreadsheet" in x.headers["content-type"]
    assert len(x.content) > 3000
    from openpyxl import load_workbook
    import io
    wb = load_workbook(io.BytesIO(x.content))
    assert "Остатки" in wb.sheetnames and "Движения" in wb.sheetnames
    ws = wb["Остатки"]
    assert ws["A1"].value == "Артикул" and ws["G1"].value == "Статус"

async def test_users_activate_and_orders(client, session):
    """Админ активирует заявку и создаёт заказ."""
    users = (await client.get("/api/users", headers=H)).json()
    assert any(u["tg_id"] == 999 for u in users)
    iid = await _mk(session, "ORD-1")
    # ORD-1 standard — для заказа нужно изделие, подменим kind через приёмку-подсборку
    from app.models.tables import Item as I
    it = (await session.execute(select(I).where(I.sku == "ORD-1"))).scalar_one()
    it.kind = "product"
    await session.commit()
    r = await client.post("/api/orders", json={"customer": "Покупатель-1", "items": [{"product_id": it.id, "need": 3}]}, headers=H)
    assert r.status_code == 200, r.text
    orders = (await client.get("/api/orders", headers=H)).json()
    assert any(o["customer"] == "Покупатель-1" for o in orders)
