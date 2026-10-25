"""Избранное: у каждого своё, друг другу не мешаем."""
from sqlalchemy import select
from app.models.tables import Folder, Item

H = {"X-Telegram-Init-Data": "dev"}

async def _mk(session, sku="FV-1"):
    fid = (await session.execute(select(Folder).where(Folder.name == "Метизы"))).scalar_one().id
    it = Item(sku=sku, name=sku, kind="standard", folder_id=fid, qty=5)
    session.add(it)
    await session.commit()
    return it.id

async def test_fav_toggle_and_mine(client, session):
    """Звездочка туда-сюда, в моём списке только моё."""
    iid = await _mk(session)
    r1 = await client.post(f"/api/favorites/{iid}", headers=H)
    assert r1.json() == {"fav": True}
    mine = (await client.get("/api/favorites", headers=H)).json()
    assert any(x["sku"] == "FV-1" for x in mine)
    r2 = await client.post(f"/api/favorites/{iid}", headers=H)
    assert r2.json() == {"fav": False}
    mine2 = (await client.get("/api/favorites", headers=H)).json()
    assert not any(x["sku"] == "FV-1" for x in mine2)
