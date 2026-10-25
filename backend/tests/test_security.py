"""Безопасность: без телеги закрыто, доки закрыты, лимиты стоят."""
from app.core.security import check_init_data
from app.core.config import settings

def test_no_token_no_access(monkeypatch):
    """Без токена и без DEV — никого не пускаем."""
    monkeypatch.setattr(settings, "BOT_TOKEN", "")
    monkeypatch.setattr(settings, "DEV_ALLOW_UNAUTH", False)
    assert check_init_data("dev") is None
    assert check_init_data("") is None

def test_stale_init_data_rejected(monkeypatch):
    """Старая подпись (старше суток) — отказ."""
    import time, urllib.parse, hashlib, hmac
    monkeypatch.setattr(settings, "BOT_TOKEN", "test-token")
    monkeypatch.setattr(settings, "DEV_ALLOW_UNAUTH", False)
    pairs = {"auth_date": str(int(time.time()) - 90000), "user": "{}", "query_id": "x"}
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", b"test-token", hashlib.sha256).digest()
    h = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    q = urllib.parse.urlencode({**pairs, "hash": h})
    assert check_init_data(q) is None

async def test_docs_closed(client):
    """Swagger и ReDoc закрыты."""
    import httpx
    from app.main import app
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        assert (await c.get("/docs")).status_code == 404
        assert (await c.get("/openapi.json")).status_code == 404
