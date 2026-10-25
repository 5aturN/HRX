"""Прод-закалка: готовность и антиспам уведомлений о низких остатках."""
import httpx
from sqlalchemy import select
from app.core.config import settings
from app.models.tables import Folder, Item

H = {"X-Telegram-Init-Data": "dev"}

async def test_ready_ok(client):
    """Проверка готовности отвечает, база жива."""
    r = await client.get("/api/ready", headers=H)
    assert r.status_code == 200 and r.json()["ok"] is True


async def test_ready_dead_db_503(client, monkeypatch):
    """Мёртвая база: готовность честно отвечает 503, а не 500."""
    import app.main as _main

    async def _dead():
        raise RuntimeError("база недоступна")

    monkeypatch.setattr(_main, "check_db", _dead)
    r = await client.get("/api/ready", headers=H)
    assert r.status_code == 503, r.text
    assert r.json()["ok"] is False


async def test_project_receipt_keeps_low_notified(client, session):
    """Приёмка в проект флаг не сбрасывает: остаток на складе не пополнился."""
    root = (await session.execute(select(Folder).where(Folder.name == "Склад"))).scalar_one()
    rnd = Folder(name="R&D проекты", parent_id=root.id, ftype="rnd")
    session.add(rnd)
    await session.flush()
    proj = Folder(name="Проект-Флаг", parent_id=rnd.id, ftype="rnd_project")
    session.add(proj)
    await session.flush()
    fid = (await session.execute(select(Folder).where(Folder.name == "Метизы"))).scalar_one().id
    it = Item(sku="LOWSPAM-2", name="Винт проектный", kind="standard",
              folder_id=fid, qty=4, threshold=5, notify_enabled=True, low_notified=True)
    session.add(it)
    await session.commit()
    iid = it.id
    pid = proj.id
    r = await client.post("/api/supplies", json={
        "supplier": "П", "target": "project", "project_folder_id": pid,
        "items": [{"kind": "standard", "sku": "LOWSPAM-2", "name": "Винт проектный",
                   "folder_id": fid, "qty": 10}]}, headers=H)
    assert r.status_code == 200, r.text
    session.expire_all()
    got = await session.get(Item, iid)
    assert got.low_notified is True, "приёмка в проект не должна сбрасывать флаг"

async def test_low_notify_antispam(client, session, monkeypatch):
    """О низком остатке пишем один раз, пополнение сбрасывает флаг."""
    fid = (await session.execute(select(Folder).where(Folder.name == "Метизы"))).scalar_one().id
    it = Item(sku="LOWSPAM-1", name="Винт редкий", kind="standard", folder_id=fid, qty=10)
    session.add(it)
    await session.commit()
    iid = it.id
    r = await client.post(f"/api/items/{iid}/threshold", json={"threshold": 5, "notify_enabled": True}, headers=H)
    assert r.status_code == 200, r.text

    calls = {"n": 0}

    class _Resp:
        status_code = 200

    class _FakeClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            calls["n"] += 1
            return _Resp()

    monkeypatch.setattr(settings, "BOT_TOKEN", "тест-токен")
    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)

    r = await client.post("/api/scrap", json={"item_id": iid, "qty": 6, "reason": "тест"}, headers=H)
    assert r.status_code == 200, r.text
    assert calls["n"] == 1
    session.expire_all()
    assert (await session.get(Item, iid)).low_notified is True

    r = await client.post("/api/scrap", json={"item_id": iid, "qty": 1, "reason": "тест"}, headers=H)
    assert r.status_code == 200, r.text
    assert calls["n"] == 1, "повторного письма быть не должно"

    r = await client.post("/api/supplies", json={
        "supplier": "П", "items": [{"kind": "standard", "sku": "LOWSPAM-1", "name": "Винт редкий",
                                    "folder_id": fid, "qty": 10}]}, headers=H)
    assert r.status_code == 200, r.text
    session.expire_all()
    got = await session.get(Item, iid)
    assert got.low_notified is False and got.qty == 13

    r = await client.post("/api/scrap", json={"item_id": iid, "qty": 9, "reason": "тест"}, headers=H)
    assert r.status_code == 200, r.text
    assert calls["n"] == 2, "после пополнения пишем заново"
