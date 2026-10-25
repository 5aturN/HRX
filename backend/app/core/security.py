"""Проверка Telegram WebApp initData по хешу и бот-токену (строгая; DEV_ALLOW_UNAUTH — только локалка)."""
import hashlib
import hmac
import logging
import urllib.parse

from .config import settings

log = logging.getLogger("hrx.security")

def check_init_data(init_data: str) -> dict | None:
    """Возвращает dict пользователя из initData либо None. Рус. логи."""
    if settings.DEV_ALLOW_UNAUTH and init_data in ("", "dev"):
        log.info("DEV-режим: пропуск проверки initData")
        return {"id": 999, "username": "dev", "first_name": "Dev"}
    if not settings.BOT_TOKEN:
        log.error("BOT_TOKEN не задан — проверка initData невозможна")
        return None
    try:
        pairs = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        recv_hash = pairs.pop("hash", "")
        data_check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
        secret = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
        calc = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, recv_hash):
            log.error("Подпись initData не сошлась")
            return None
        log.info("initData проверена успешно")
        import json
        return json.loads(pairs.get("user", "{}"))
    except Exception:
        log.exception("Ошибка проверки initData")
        return None
