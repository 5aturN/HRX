"""Лимит запросов + заголовки безопасности."""
import logging
import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

log = logging.getLogger("hrx.limits")
_hits: dict[str, list[float]] = defaultdict(list)

class RateLimit(BaseHTTPMiddleware):
    """Не больше N запросов в минуту с одного IP на API."""
    def __init__(self, app, per_min: int = 120):
        super().__init__(app)
        self.per_min = per_min

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/api/"):
            ip = request.client.host if request.client else "?"
            now = time.time()
            box = _hits[ip]
            box[:] = [t for t in box if now - t < 60]
            if len(box) >= self.per_min:
                log.error("Лимит с IP %s", ip)
                from fastapi.responses import JSONResponse
                return JSONResponse({"detail": "Слишком много запросов, подождите минуту"}, status_code=429)
            box.append(now)
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp
