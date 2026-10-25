"""Каталог: эталон подставляет название и фото."""
from sqlalchemy import select
from app.models.tables import Folder, Item, StdCatalog

H = {"X-Telegram-Init-Data": "dev"}

async def test_catalog_autofill(client, session):
    """Выбрал DIN912 — название и фото подтянулись сами."""
    r = await client.post("/api/catalog", json={"code": "DIN912", "title": "Винт с цилиндрической головкой"}, headers=H)
    assert r.status_code == 200, r.text
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGB", (50, 50), "gray").save(buf, "PNG")
    ph = await client.post("/api/catalog/DIN912/photo", files={"file": ("p.png", buf.getvalue(), "image/png")}, headers=H)
    assert ph.status_code == 200, ph.text
    fid = (await session.execute(select(Folder).where(Folder.name == "Метизы"))).scalar_one().id
    s = await client.post("/api/supplies", json={"supplier": "П", "items": [{"kind": "standard", "sku": "VINT-1", "name": "", "folder_id": fid, "qty": 10, "std_code": "din912"}]}, headers=H)
    assert s.status_code == 200, s.text
    session.expire_all()
    it = (await session.execute(select(Item).where(Item.sku == "VINT-1"))).scalar_one()
    assert "цилиндрической" in it.name and it.photo_path

async def test_catalog_list(client, session):
    """Список эталонов виден."""
    await client.post("/api/catalog", json={"code": "ISO7380", "title": "Винт с полукруглой головкой"}, headers=H)
    rows = (await client.get("/api/catalog", headers=H)).json()
    assert any(x["code"] == "ISO7380" for x in rows)
