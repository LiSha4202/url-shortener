import sys
import pytest
import asyncio

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# добавляем путь к папке src для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from core.database.base import Base
import models  # регистрируем модели

# Тестовая БД, чтобы не трогать основную
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@test-db:5432/test_db"


@pytest.fixture
def jwt_mock_settings():
    """Фикстура для мокирования JWT-настроек"""
    with patch("src.utils.create_jwt_token.settings") as mock:
        mock.jwt.jwt_secret_key = "test_secret_key"
        yield mock


@pytest.fixture(scope="function")
async def engine():
    """Фикстура для создания движка БД"""
    engine = create_async_engine(TEST_DATABASE_URL)  # создание движка
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # создание таблиц
    yield engine  # возвращаем объект Engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # создание таблиц
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine):
    """Фикстура для создания сессий БД"""
    async with engine.connect() as conn:
        trans = await conn.begin()
        async_session = AsyncSession(bind=conn, expire_on_commit=False)
        yield async_session
        await trans.rollback()
        await async_session.close()
        await conn.close()


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
    await db_session.flush()  # Коммитим, чтобы получить ID
    await db_session.refresh(new_link)

    return new_link
