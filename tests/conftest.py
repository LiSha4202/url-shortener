from unittest.mock import patch

import pytest


@pytest.fixture
def jwt_mock_settings():
    """Фикстура для мокирования JWT-настроек"""
    with patch("src.utils.create_jwt_token.settings") as mock:
        mock.jwt.jwt_secret_key = "test_secret_key"
        yield mock
