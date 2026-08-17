import sys
import pytest
import asyncio

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import ASGITransport, AsyncClient

# добавляем путь к папке src для импорта
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from core.database.engine import db_engine
from main import app

from core.database.base import Base
import models  # регистрируем модели

# Тестовая БД, чтобы не трогать основную
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@test-db:5432/test_db"


@pytest.fixture(autouse=True)
def mock_redis():
    with (
        patch("crud.link_crud.redis_client", new_callable=AsyncMock) as mock_link,
        patch("crud.click_crud.redis_client", new_callable=AsyncMock) as mock_click,
        patch("utils.redis_cache.redis_client", new_callable=AsyncMock) as mock_cache,
    ):
        # Настраиваем все моки одинаково
        for mock in (mock_link, mock_click, mock_cache):
            mock.get = AsyncMock(return_value=None)
            mock.setex = AsyncMock(return_value=True)
            mock.delete = AsyncMock(return_value=True)
        yield mock_link  # можно вернуть любой


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


@pytest.fixture(scope="function")
async def mock_link_crud_settings():
    """Мокает настройки для тестов ссылок"""
    settings_mock = MagicMock()
    settings_mock.ls.short_code_max_length = 16
    settings_mock.ls.short_code_min_length = 4
    settings_mock.ls.expire_in_days_min_length = 1
    settings_mock.ls.expire_in_days_max_length = 365

    with patch("src.crud.link_crud.settings", settings_mock):
        yield settings_mock


@pytest.fixture(scope="function")
async def create_user(db_session):
    """Создание тестового пользователя"""
    from models.users_model import User
    from utils.hash_password import get_password_hash

    new_user = User(
        username="Test",
        email="test@example.com",
        password=get_password_hash("password"),
    )
    db_session.add(new_user)
    await db_session.flush()
    await db_session.refresh(new_user)

    return new_user


@pytest.fixture(scope="function")
async def client(engine):
    # Переопределяем зависимость, чтобы эндпоинты использовали сессии от тестового движка
    async def override_scoped_session():
        # Используем стандартный async_sessionmaker от движка
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with async_session() as session:
            yield session

    app.dependency_overrides[db_engine.scoped_session_dependency] = (
        override_scoped_session
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Убираем переопределение после теста
    app.dependency_overrides.pop(db_engine.scoped_session_dependency, None)
