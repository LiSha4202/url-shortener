import sys
import pytest


from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unittest.mock import patch

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.database.base import Base

import models

# Тестовая БД, чтобы не трогать основную
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@test-db:5433/test_db"


@pytest.fixture
def jwt_mock_settings():
    """Фикстура для мокирования JWT-настроек"""
    with patch("src.utils.create_jwt_token.settings") as mock:
        mock.jwt.jwt_secret_key = "test_secret_key"
        yield mock


@pytest.fixture(scope="session")
async def engine():
    """Фикстура для создания движка БД"""
    engine = create_async_engine(TEST_DATABASE_URL)  # создание движка
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # создание таблиц
    yield engine  # возвращаем объект Engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # создание таблиц


@pytest.fixture(scope="function")
async def db_session(engine):
    """Фикстура для создания сессий БД"""
    async with engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        async_session = async_sessionmaker(bind=conn, expire_on_commit=False)
        session = async_session()
        yield session
        await session.close()
        await conn.rollback()


@pytest.fixture(scope="function")
async def created_link(db_session):
    """Создаёт ссылку для тестированияи гарантирует её наличие"""
    from models import Link

    # Создаём новый объект ссылки
    new_link = Link(
        short_code="test123",
        original_url="https://example.com",
    )
    db_session.add(new_link)
    await db_session.commit()  # Коммитим, чтобы получить ID
    await db_session.refresh(new_link)

    return new_link
