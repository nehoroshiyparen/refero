import uuid
import logging
import os
import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from collections.abc import AsyncGenerator

from app.infrastructure.database import Base
from app.core.config import settings

pytestmark = pytest.mark.asyncio

# ── Logging ───────────────────────────────────────────────────
logger = logging.getLogger("test_conftest")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine():
    logger.debug(f"Creating test engine: {settings.TEST_DATABASE_URL}")
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    yield engine
    logger.debug("Disposing test engine")
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def setup_database(test_engine):
    from alembic.config import Config
    from alembic import command

    logger.debug("setup_database: running migrations + seeding")

    async with test_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))

    # env.py делает config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    # поэтому подменяем прямо в settings
    original_url = settings.DATABASE_URL
    settings.DATABASE_URL = settings.TEST_DATABASE_URL

    try:
        # command.upgrade вызывает env.py, где asyncio.run() создаёт свой loop
        # поэтому запускаем в отдельном треде, чтобы не конфликтовать с текущим loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: command.upgrade(Config("alembic.ini"), "head"),
        )
    finally:
        settings.DATABASE_URL = original_url

    # Сидируем справочники
    async with test_engine.begin() as conn:
        for s in ["DRAFT", "PENDING_APPROVAL", "REVIEW", "PUBLISHED", "REJECTED"]:
            await conn.execute(
                text("INSERT INTO article_statuses (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                {"name": s},
            )
        for s in ["PENDING", "APPROVED", "REJECTED"]:
            await conn.execute(
                text("INSERT INTO approval_statuses (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                {"name": s},
            )
        for s in ["PENDING", "APPROVED", "REJECTED", "REQUESTING_CHANGES"]:
            await conn.execute(
                text("INSERT INTO review_statuses (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                {"name": s},
            )

    yield

    # Ядерная зачистка тестовой БД
    async with test_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(test_engine, setup_database) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    
    async with session_factory() as session:
        await session.execute(text("INSERT INTO roles (name) VALUES ('AUTHOR') ON CONFLICT (name) DO NOTHING"))
        await session.execute(text("INSERT INTO roles (name) VALUES ('REVIEWER') ON CONFLICT (name) DO NOTHING"))
        await session.execute(text("INSERT INTO roles (name) VALUES ('ADMIN') ON CONFLICT (name) DO NOTHING"))
        await session.commit()

        yield session

        await session.rollback()


@pytest_asyncio.fixture(loop_scope="session")
async def test_user(db_session: AsyncSession) -> dict:
    from app.modules.users.models.user import User

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username=f"test_author_{user_id.hex[:8]}",
        email=f"test_{user_id.hex[:8]}@test.com",
        hashed_password="fake_hash",
        full_name="Test Author",
        role_name="AUTHOR",
    )
    db_session.add(user)
    await db_session.flush()

    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }


@pytest_asyncio.fixture(loop_scope="session")
async def test_coauthor(db_session: AsyncSession) -> dict:
    from app.modules.users.models.user import User

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username=f"test_coauthor_{user_id.hex[:8]}",
        email=f"coauthor_{user_id.hex[:8]}@test.com",
        hashed_password="fake_hash",
        full_name="Test Co-Author",
        role_name="AUTHOR",
    )
    db_session.add(user)
    await db_session.flush()

    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }


@pytest_asyncio.fixture(loop_scope="session")
async def test_coauthor2(db_session: AsyncSession) -> dict:
    from app.modules.users.models.user import User

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username=f"test_coauthor2_{user_id.hex[:8]}",
        email=f"coauthor2_{user_id.hex[:8]}@test.com",
        hashed_password="fake_hash",
        full_name="Test Co-Author 2",
        role_name="AUTHOR",
    )
    db_session.add(user)
    await db_session.flush()

    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }


@pytest_asyncio.fixture(loop_scope="session")
async def test_reviewer(db_session: AsyncSession) -> dict:
    from app.modules.users.models.user import User

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username=f"test_reviewer_{user_id.hex[:8]}",
        email=f"reviewer_{user_id.hex[:8]}@test.com",
        hashed_password="fake_hash",
        full_name="Test Reviewer",
        role_name="REVIEWER",
    )
    db_session.add(user)
    await db_session.flush()

    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }