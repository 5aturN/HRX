"""Общие зависимости роутов: проверка initData, текущий пользователь, его роли."""
import logging
from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.core.security import check_init_data
from app.models.tables import User, UserRole

log = logging.getLogger("hrx.deps")

async def current_user(request: Request, x_telegram_init_data: str = Header(default=""), session: AsyncSession = Depends(get_session)) -> User:
    """Достаёт юзера по initData. В DEV-режиме создаёт/находит dev-юзера."""
    data = check_init_data(x_telegram_init_data)
    if not data:
        raise HTTPException(status_code=401, detail="Нет доступа: откройте через Telegram")
    tg_id = int(data.get("id", 0))
    user = (await session.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
    if user is None:
        user = User(tg_id=tg_id, username=data.get("username"), first_name=data.get("first_name"), status="pending")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        log.info("Новый пользователь tg_id=%s, ждёт активации", tg_id)
    if user.status == "blocked":
        raise HTTPException(status_code=403, detail="Доступ закрыт, обратитесь к админу")
    if user.status == "pending" and request.url.path != "/api/me":
        raise HTTPException(status_code=403, detail="Аккаунт на проверке: дождитесь активации админом")
    return user

async def user_roles(user: User = Depends(current_user), session: AsyncSession = Depends(get_session)) -> list[str]:
    """Список ролей юзера."""
    rows = (await session.execute(select(UserRole.role).where(UserRole.user_id == user.id))).all()
    return [r[0] for r in rows]

def need_roles(*allowed: str):
    """Проверяет, что у юзера есть хоть одна из ролей."""
    async def _check(roles: list[str] = Depends(user_roles)) -> list[str]:
        if "admin" in roles:
            return roles
        if not any(r in roles for r in allowed):
            raise HTTPException(status_code=403, detail="Нужны права: " + ", ".join(allowed))
        return roles
    return _check
