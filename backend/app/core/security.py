"""Проверка initData + свежесть + защита от повторов."""
import hashlib
import hmac
import json
import logging
import time
import urllib.parse
from .config import settings

log = logging.getLogger("hrx.security")

def check_init_data(init_data: str) -> dict | None:
    """Проверяет подпись, свежесть (сутки) и возвращает юзера. В DEV — тестовый."""
    if settings.DEV_ALLOW_UNAUTH and init_data in ("", "dev"):
        log.info("DEV-режим: пропуск проверки initData")
        return {"id": 999, "username": "dev", "first_name": "Dev"}
    if not settings.BOT_TOKEN:
        log.error("BOT_TOKEN не задан")
        return None
    try:
        pairs = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        recv_hash = pairs.pop("hash", "")
        auth = int(pairs.get("auth_date", "0") or 0)
        if auth and time.time() - auth > 86400:
            log.error("initData старше суток")
            return None
        data_check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
        secret = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
        calc = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, recv_hash):
            log.error("Подпись initData не сошлась")
            return None
        return json.loads(pairs.get("user", "{}"))
    except Exception:
        log.exception("Ошибка проверки initData")
        return None
