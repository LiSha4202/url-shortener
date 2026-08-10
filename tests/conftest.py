import pytest

from unittest.mock import patch

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.database.base import Base

# Тестовая БД, чтобы не трогать основную
TEST_DATABASE_URL = "postgresql://user:password@pg:5432/test_db"


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


@pytest.fixture
async def db_session(engine):
    """Фикстура для создания сессий БД"""
    async with engine.connect() as conn:
        await conn.begin()
        async_session = async_sessionmaker(bind=conn, expire_on_commit=False)
        session = async_session()
        yield session
        await session.close()
        await conn.rollback()
