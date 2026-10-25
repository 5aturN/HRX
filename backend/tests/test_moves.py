"""Тесты движений: брак, возврат, выдача в проект, химия."""
from sqlalchemy import select
from app.models.tables import Folder, Item, StockMove

H = {"X-Telegram-Init-Data": "dev"}

async def _mk(session, sku, qty=20, kind="standard") -> int:
    fid = (await session.execute(select(Folder).where(Folder.name == "Метизы"))).scalar_one().id
    it = Item(sku=sku, name=sku, kind=kind, folder_id=fid, qty=qty)
    session.add(it)
    await session.commit()
    return it.id

async def test_scrap_needs_reason(client, session):
    """Без причины в брак не списываем."""
    iid = await _mk(session, "BR-1")
    r = await client.post("/api/scrap", json={"item_id": iid, "qty": 1}, headers=H)
    assert r.status_code == 400 and "причину" in r.text

async def test_scrap_and_unscrap(client, session):
    """Брак минусует, возврат плюсует, журнал пишется."""
    iid = await _mk(session, "BR-2")
    r = await client.post("/api/scrap", json={"item_id": iid, "qty": 5, "reason": "кривой"}, headers=H)
    assert r.status_code == 200 and r.json()["qty"] == 15
    r2 = await client.post("/api/unscrap", json={"item_id": iid, "qty": 2, "reason": "ошиблись"}, headers=H)
    assert r2.json()["qty"] == 17
    session.expire_all()
    moves = (await session.execute(select(StockMove).where(StockMove.item_id == iid))).scalars().all()
    assert {m.mtype for m in moves} == {"brak", "vozvrat"}

async def test_scrap_more_than_have_rejected(client, session):
    """Больше остатка в брак не отдаём."""
    iid = await _mk(session, "BR-3", qty=2)
    r = await client.post("/api/scrap", json={"item_id": iid, "qty": 5, "reason": "x"}, headers=H)
    assert r.status_code == 400

async def test_to_project_and_chem(client, session):
    """Выдача в проект и списание химии."""
    iid = await _mk(session, "RD-1")
    root = (await session.execute(select(Folder).where(Folder.name == "Склад"))).scalar_one()
    rnd = Folder(name="R&D проекты", parent_id=root.id, ftype="rnd")
    session.add(rnd)
    await session.flush()
    proj = Folder(name="Тест-проект", parent_id=rnd.id, ftype="rnd_project")
    session.add(proj)
    await session.commit()
    pid = proj.id
    r = await client.post("/api/to-project", json={"item_id": iid, "qty": 4, "project_folder_id": pid}, headers=H)
    assert r.status_code == 200 and r.json()["qty"] == 16
    ch = await _mk(session, "CH-1", qty=5)
    r2 = await client.post("/api/chem-out", json={"item_id": ch, "qty": 1}, headers=H)
    assert r2.json()["qty"] == 4
