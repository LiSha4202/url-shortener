import pytest
from datetime import datetime
from pydantic import ValidationError

from src.core.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserModel,
)
from src.core.schemas.link_schema import LinkCreate, LinkResponse, LinkUpdate
from src.core.config import settings


class TestUserSchemas:
    """Тесты для схем User и Link"""

    # --- Test UserCreate ---
    def test_user_create_valid(self):
        """Проверка валидного создания пользователя"""
        user_data = {
            "username": "valid_user",
            "email": "test@example.com",
            "password": "strongpassword123",
        }
        user = UserCreate(**user_data)
        assert user.username == "valid_user"
        assert user.email == "test@example.com"
        # Пароль в ответе может быть скрыт или приведён к типу str, проверяем наличие
        assert user.password is not None

    def test_user_create_short_name(self):
        """Проверка, что имя пользователя меньше минимальной длины вызывает ошибку"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",
                email="test@example.com",
                password="strongpassword123",
            )
            assert "username" in str(exc_info.value)

    def test_user_create_short_password(self):
        """Проверка, что пароль короче минимальной длины вызывает ошибку"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="valid_user",
                email="user@example.com",
                password="123",
            )
        assert "password" in str(exc_info.value)

    def test_user_create_invalid_email(self):
        """Проверка невалидного email"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="valid_user",
                email="not-an-email",
                password="strongpassword123",
            )

    # --- Test UserUpdate ---
    def test_user_update_partial(self):
        """Обновление только поля username"""
        update_data = {"username": "new_username"}
        user_update = UserUpdate(**update_data)
        assert user_update.username == "new_username"
        assert user_update.email is None
        assert user_update.password is None

    def test_user_update_forbid_extra(self):
        """Проверка, что extra поля запрещены (extra="forbid")"""

        with pytest.raises(ValidationError):
            UserUpdate(  # type: ignore
                username="test",
                field_that_does_not_exist="bad_value",  # type: ignore
            )

    # --- Test UserModel & Response (Mocking ORM behaviour if needed, but mostly validation) ---
    def test_user_model_creation(self):
        """Создание полной модели пользователя"""
        model_data = {
            "id": "123",
            "username": "test_user",
            "email": "test@example.com",
            "created_at": datetime.utcnow(),
        }
        user = UserModel(**model_data)
        assert user.id == "123"
        assert isinstance(user.created_at, datetime)


class TestLinkSchemas:
    """Тесты для схем ссылок"""

    # --- Test LinkCreate ---
    def test_link_create_valid_generated_code(self):
        """Создание ссылки без короткого кода"""
        link_data = {
            "original_url": "https://www.google.com",
            # short_code отсутствует
        }
        link = LinkCreate(**link_data)  # type: ignore
        assert link.short_code == "my-link-1"

    def test_link_create_custom_code_valid(self):
        """Создание ссылки с валидным кастомным кодом"""
        link_data = {
            "original_url": "https://example.com",
            "short_code": "my-link-1",
        }
        link = LinkCreate(**link_data)  # type: ignore
        assert link.short_code == "my-link-1"

    def test_link_create_custom_code_invalid(self):
        """Создание ссылки с невалидным кодом (содержит пробел или спецсимволы)"""
        with pytest.raises(ValidationError):
            LinkCreate(
                original_url="https://www.google.com",  # type: ignore
                short_code="bad code",
            )

    def test_link_create_expires_at_bounds(self):
        """Проверка границ expires_at"""
        # Минимальное значение
        min_days = settings.ls.expire_in_days_min_length
        # Максимальное значение
        max_days = settings.ls.expire_in_days_max_length

        # Валидный минимум
        link_min = LinkCreate(
            original_url="https://www.google.com",  # type: ignore
            expires_at=min_days,
        )
        assert link_min.expires_at == min_days

        # Валидный максимум
        link_max = LinkCreate(
            original_url="https://www.google.com",  # type: ignore
            expires_at=max_days,
        )
        assert link_max.expires_at == max_days

        # Слишком мало
        with pytest.raises(ValidationError):
            LinkCreate(  # type: ignore
                original_url="https://www.google.com", expires_at=min_days - 1
            )

        # Слишком много
        with pytest.raises(ValidationError):
            LinkCreate(  # type: ignore
                original_url="https://www.google.com", expires_at=max_days + 1
            )

    # --- Test LinkResponse ---
    def test_link_response_short_url(self):
        """Проверка вычисленного поля short_url"""
        # Mock settings, так как в тестовой среде хост/порт могут не совпадать или отсутствовать
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(settings.run, "host", "0.0.0.0")
            mp.setattr(settings.run, "port", "8000")

            link_data = {
                "short_code": "abc123",
                "original_url": "https://example.com",
                "created_at": datetime.utcnow(),
            }
            response = LinkResponse(**link_data)

            expected_url = "http://0.0.0.0:8000/abc123"
            assert response.short_url == expected_url

    def test_link_response_default_created_at(self):
        """Проверка, что created_at генерируется автоматически, если не передан"""
        link_data = {
            "short_code": "abc123",
            "original_url": "https://example.com",
        }
        response = LinkResponse(**link_data)  # type: ignore
        assert response.created_at is not None
        assert isinstance(response.created_at, datetime)

    # --- Test LinkUpdate ---
    def test_link_update_valid(self):
        """Валидное обновление ссылки"""
        update_data = {"original_url": "https://new_url.com"}
        link_update = LinkUpdate(**update_data)  # type: ignore
        assert link_update.original_url is not None

    def test_link_update_invalid_expires(self):
        """Невалидное время истечения в обновлении (должен вызывать исключение из exc_400_bad_req_exp_link)"""
        # Здесь важно: validate_expires_At должен raise исключение.
        # Если exc_400_bad_req_exp_link - это HTTPException, то Pydantic валидаторы
        # обычно ловят ValidationError, но если raise exception outside Pydantic logic,
        # то тест может провалиться иначе.
        # Обычно для FastAPI лучше возвращать HTTPException из валидаторов в тестах
        # нужно ловить конкретное исключение или проверять логику через mock.

        # Предположим, exc_400_bad_req_exp_link - это HTTPException
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            LinkUpdate(
                expires_at=settings.ls.expire_in_days_min_length,
            )

    def test_link_update_forbid_extra(self):
        """Проверка запрета лишних полей"""
        with pytest.raises(ValidationError):
            LinkUpdate(
                original_url="https://new.com",
                bad_field="value",  # type: ignore
            )
