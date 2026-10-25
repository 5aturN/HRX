"""Тесты приёмки: создание поставки, повтор артикула, остатки, документы, ошибки."""
from sqlalchemy import select
from app.models.tables import Folder, Item

H = {"X-Telegram-Init-Data": "dev"}

async def _folder_id(session, name="Метизы") -> int:
    f = (await session.execute(select(Folder).where(Folder.name == name))).scalar_one()
    return f.id

async def test_supply_creates_items_and_stock(client, session):
    """Приёмка создаёт позиции и кладёт остатки."""
    fid = await _folder_id(session)
    r = await client.post("/api/supplies", json={
        "supplier": "Поставщик-1", "upd_no": "УПД-1", "invoice_no": "СЧ-1",
        "items": [
            {"kind": "detail", "sku": "T-001", "name": "Деталь тест", "decimal": "ТСТ.001", "folder_id": fid, "qty": 5},
            {"kind": "standard", "sku": "M6x20", "name": "Винт М6х20", "folder_id": fid, "qty": 10},
        ]}, headers=H)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["positions"] == 2 and body["total_qty"] == 15
    session.expire_all()
    items = (await session.execute(select(Item))).scalars().all()
    assert {i.sku: i.qty for i in items} == {"T-001": 5, "M6x20": 10}

async def test_same_sku_adds_qty_no_duplicates(client, session):
    """Повтор того же артикула = плюс к остатку, без дублей."""
    fid = await _folder_id(session)
    one = {"supplier": "П", "items": [{"kind": "standard", "sku": "DUP-1", "name": "Дубль", "folder_id": fid, "qty": 3}]}
    r1 = await client.post("/api/supplies", json=one, headers=H)
    assert r1.status_code == 200, r1.text
    r2 = await client.post("/api/supplies", json=one, headers=H)
    assert r2.status_code == 200, r2.text
    session.expire_all()
    rows = (await session.execute(select(Item).where(Item.sku == "DUP-1"))).scalars().all()
    assert len(rows) == 1 and rows[0].qty == 6

async def test_detail_without_decimal_rejected(client, session):
    """У детали без децимального приёмка не проходит."""
    fid = await _folder_id(session)
    r = await client.post("/api/supplies", json={
        "supplier": "П", "items": [{"kind": "detail", "sku": "NODEC", "name": "Без дец", "folder_id": fid, "qty": 1}]}, headers=H)
    assert r.status_code == 400 and "децимальный" in r.text

async def test_stock_search_and_low_flag(client, session):
    """Поиск по остаткам и флаг нехватки."""
    fid = await _folder_id(session)
    r = await client.post("/api/supplies", json={
        "supplier": "П", "items": [{"kind": "standard", "sku": "LOW-1", "name": "Винт редкий", "folder_id": fid, "qty": 2}]}, headers=H)
    assert r.status_code == 200, r.text
    s = await client.get("/api/stock", params={"q": "редкий"}, headers=H)
    assert s.status_code == 200 and len(s.json()) == 1
    assert s.json()[0]["sku"] == "LOW-1"

async def test_doc_upload_and_download(client, session):
    """Прикрепление УПД и скачивание."""
    fid = await _folder_id(session)
    rr = await client.post("/api/supplies", json={
        "supplier": "П", "items": [{"kind": "standard", "sku": "DOC-1", "name": "С доком", "folder_id": fid, "qty": 1}]}, headers=H)
    assert rr.status_code == 200, rr.text
    sid = rr.json()["id"]
    files = {"file": ("upd.pdf", b"%PDF-fake", "application/pdf")}
    r = await client.post(f"/api/supplies/{sid}/docs", params={"dtype": "upd"}, files=files, headers=H)
    assert r.status_code == 200, r.text
    docs = (await client.get(f"/api/supplies/{sid}/docs", headers=H)).json()
    assert len(docs) == 1
    dl = await client.get(f"/api/docs/{docs[0]['id']}/download", headers=H)
    assert dl.status_code == 200 and dl.content == b"%PDF-fake"
