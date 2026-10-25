"""Лимит запросов + заголовки безопасности."""
from __future__ import annotations

import logging
import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

log = logging.getLogger("hrx.limits")
_hits: dict[str, list[float]] = defaultdict(list)
_last_sweep: float = 0.0

# Health не лимитируем: его дёргают Docker, Caddy и мониторинг.
_SKIP_PREFIXES = ("/api/health", "/api/ready")


class RateLimit(BaseHTTPMiddleware):
    """Не больше N запросов в минуту с одного IP на API."""

    def __init__(self, app, per_min: int = 120):
        super().__init__(app)
        self.per_min = per_min

    async def dispatch(self, request, call_next):
        path = request.url.path
        if path.startswith("/api/") and not path.startswith(_SKIP_PREFIXES):
            ip = request.client.host if request.client else "?"
            now = time.time()
            box = _hits[ip]
            box[:] = [t for t in box if now - t < 60]
            if len(box) >= self.per_min:
                log.error("Лимит с IP %s", ip)
                return JSONResponse(
                    {"detail": "Слишком много запросов, подождите минуту"}, status_code=429
                )
            box.append(now)
            global _last_sweep
            if now - _last_sweep > 300:
                _last_sweep = now
                for key in list(_hits.keys()):
                    _hits[key][:] = [t for t in _hits[key] if now - t < 60]
                    if not _hits[key]:
                        del _hits[key]
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        return resp
