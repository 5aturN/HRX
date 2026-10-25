"""Фикстуры тестов: отдельная БД в памяти, тестовый юзер с ролями."""
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from fastapi.testclient import TestClient
from app.core.db import Base
import app.models  # noqa: F401
from app.main import app
from app.core.db import get_session
from app.models.tables import Folder, User, UserRole

@pytest_asyncio.fixture
async def session():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with eng.begin() as c:
        await c.run_sync(Base.metadata.create_all)
    mk = async_sessionmaker(eng, expire_on_commit=False)
    async with mk() as s:
        root = Folder(name="Склад", ftype="root")
        s.add(root)
        await s.flush()
        met = Folder(name="Метизы", parent_id=root.id, ftype="consumable_type")
        s.add(met)
        await s.flush()
        u = User(tg_id=999, username="dev", first_name="Dev", status="active")
        s.add(u)
        await s.flush()
        s.add_all([UserRole(user_id=u.id, role="worker"), UserRole(user_id=u.id, role="admin")])
        await s.commit()
        yield s
    await eng.dispose()

@pytest_asyncio.fixture
async def client(session):
    async def _sess():
        yield session
    app.dependency_overrides[get_session] = _sess
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
