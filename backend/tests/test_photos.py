"""Фото, дерево папок, кабинет."""
import io
from PIL import Image
from sqlalchemy import select
from app.models.tables import Folder, Item

H = {"X-Telegram-Init-Data": "dev"}

def _png(color="red") -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color).save(buf, "PNG")
    return buf.getvalue()

async def _mk(session, sku="PH-1", qty=5):
    fid = (await session.execute(select(Folder).where(Folder.name == "Метизы"))).scalar_one().id
    it = Item(sku=sku, name=sku, kind="standard", folder_id=fid, qty=qty)
    session.add(it)
    await session.commit()
    return it.id

async def test_item_photo_upload_and_get(client, session):
    """Фото позиции грузится и отдаётся."""
    iid = await _mk(session)
    r = await client.post(f"/api/items/{iid}/photo", files={"file": ("p.png", _png(), "image/png")}, headers=H)
    assert r.status_code == 200, r.text
    g = await client.get(f"/api/items/{iid}/photo", headers=H)
    assert g.status_code == 200 and g.headers["content-type"] == "image/jpeg"
    s = await client.get("/api/stock", params={"q": "PH-1"}, headers=H)
    assert s.json()[0]["has_photo"] is True

async def test_avatar_and_me(client, session):
    """Аватар и кабинет: профиль, роли, статистика."""
    r = await client.post("/api/me/avatar", files={"file": ("a.png", _png("blue"), "image/png")}, headers=H)
    assert r.status_code == 200, r.text
    me = (await client.get("/api/me", headers=H)).json()
    assert me["has_avatar"] is True and "worker" in me["roles"]
    assert "week_moves" in me

async def test_folders_tree(client, session):
    """Дерево папок: корень, дети, счётчики."""
    await _mk(session, sku="TR-1")
    t = (await client.get("/api/folders/tree", headers=H)).json()
    assert len(t) == 1 and t[0]["name"] == "Склад"
    assert t[0]["n_items"] >= 1 and t[0]["qty"] >= 5
    kids = {c["name"] for c in t[0]["children"]}
    assert "Метизы" in kids
