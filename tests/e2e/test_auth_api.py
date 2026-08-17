import pytest
import httpx
from httpx import ASGITransport, AsyncClient

from models import User
from crud.user_crud import create_user as crud_cu
from core.schemas.user_schema import UserCreate
from core.database.engine import db_engine
from core.config import settings

from main import app


@pytest.mark.asyncio
class TestAuthAPI:

    async def _register(self, client, username, email, password):
        """Вспомогательный метод для регистрации пользователя."""
        payload = {
            "username": username,
            "email": email,
            "password": password,
        }
        return await client.post("/auth/register", json=payload)

    async def test_register_success(self, client):
        """Тест успешной регистрации пользователя"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:

            payload = {
                "username": "test_user",
                "email": "test@example.com",
                "password": "password",
            }

            response = await ac.post("/auth/register", json=payload)

            assert response.status_code == 201
            data = response.json()

            assert data["username"] == "test_user"
            assert data["email"] == "test@example.com"

    async def test_register_duplicate_email(self, client):
        """Тест регистрации с уже существующиим email"""

        # регистрируем пользователя
        response1 = await self._register(
            client, "test_user", "test@example.com", "password"
        )
        assert response1.status_code == 201

        # регистрируем второго пользователя
        response2 = await self._register(
            client, "test_user2", "test@example.com", "password2"
        )
        assert response2.status_code == 409

    async def test_login_success(self, client):
        """Тест успешного входа и получения токенов"""

        # Регистрация пользователя
        await self._register(
            client,
            "test_user",
            "test@example.com",
            "password",
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:

            # OAuth2 PAssword Flow Требует form-data
            data = {
                "username": "test@example.com",
                "password": "password",
            }

            response = await ac.post("/auth/login", data=data)

            assert response.status_code == 200
            json_response = response.json()

            assert "access_token" in json_response
            assert "refresh_token" in json_response
            assert json_response["token_type"] == "bearer"

            assert "access_token" in ac.cookies or settings.sc.key
