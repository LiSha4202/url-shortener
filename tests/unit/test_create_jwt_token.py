from unittest.mock import patch

from datetime import timedelta, datetime, timezone
from jose import jwt

from tests.conftest import jwt_mock_settings

from src.utils.create_jwt_token import create_access_jwt_token, create_refresh_jwt_token


class TestCreateAccessJWTToken:

    def test_create_access_token_success(self, jwt_mock_settings):
        """Тест успешного создания access-токена"""
        data = {"sub": "user_id_123", "role": "admin"}
        expires_time = 15  # время жизни токенов в минутах

        token = create_access_jwt_token(
            data=data,
            expires_time=expires_time,
            jwt_algorithm="HS256",
        )

        # Проверяем, что токен не пустой
        assert token is not None
        assert isinstance(token, str)

        # Декодируем JWT
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])

        # Проверяем, что исходные данные сохранились
        assert payload["sub"] == "user_id_123"
        assert payload["role"] == "admin"
        assert "exp" in payload

        # Проверка expiratiom time (Должно быть примерно сейчас + 15 минут)
        now = datetime.now(timezone.utc)
        expected_exp = (now + (timedelta(minutes=expires_time))).timestamp()

        print(f"payload['exp'] = {payload['exp']}")
        print(f"expected_exp    = {expected_exp}")
        print(f"difference      = {abs(payload['exp'] - expected_exp)}")
        # Допускаем погрешность 20 секунд
        assert abs(payload["exp"] - expected_exp) < 10

    def test_create_access_token_with_expires_delta(self, jwt_mock_settings):
        """Тест создания токена с явным timedelta"""

        data = {"user": "test"}
        expires_delta = timedelta(hours=1)

        token = create_access_jwt_token(
            data=data,
            expires_time=15,  # этот аргумент игнорируется, если передан expires_delta
            jwt_algorithm="HS256",
            expires_delta=expires_delta,
        )

        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["user"] == "test"

        expected_exp = datetime.now(timezone.utc) + timedelta(hours=1)
        diff = payload["exp"] - expected_exp.timestamp()

        assert (
            abs(diff) < 10
        ), f"Token expiration is not within the acceptable range: {diff}"


class TestCreateRefreshJWTToken:
    def test_create_refresh_token_success(self, jwt_mock_settings):
        """Тест успешного создания refresh-токена"""

        data = {"sub": "user_id_123", "token_type": "refresh"}
        expires_time = 7  # days

        token = create_refresh_jwt_token(
            data=data,
            expires_time=expires_time,
            jwt_algorithm="HS256",
        )

        assert token is not None
        assert isinstance(token, str)

        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])

        assert payload["sub"] == "user_id_123"
        assert payload["token_type"] == "refresh"

        # Проверяем expiration time (должно быть сейчас + 7 дней)
        assert "exp" in payload
        expected_exp = datetime.now(timezone.utc) + timedelta(days=expires_time)
        assert abs(payload["exp"] - expected_exp.timestamp()) < 10

    def test_create_refresh_token_with_expires_delta(self, jwt_mock_settings):
        """Тест создания токена с явным timedelta"""
        data = {"user": "test"}
        expires_delta = timedelta(days=30)

        token = create_refresh_jwt_token(
            data=data,
            expires_time=7,  # этот аргумент игнорируется, если передан expires_delta
            jwt_algorithm="HS256",
            expires_delta=expires_delta,
        )

        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["user"] == "test"

        expected_exp = datetime.now() + timedelta(days=30)
        assert abs(payload["exp"] - expected_exp.timestamp()) < 60
