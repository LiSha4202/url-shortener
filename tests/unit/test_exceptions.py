import pytest
from unittest.mock import patch

from fastapi import HTTPException

from src.core.exceptions import (
    exc_401_not_val_cred,
    exc_link_404_not_found,
    exc_link_410_gone,
    exc_log_click_500_server_error,
    exc_short_code_existing,
    exc_400_expires_not_provided,
    exc_401_user_not_auth,
    exc_403_user_forbidden_to_link,
    exc_404_user_not_found,
    exc_400_bad_request_patch,
    exc_400_bad_req_exp_link,
    exc_403_admin_forbidden,
    exc_redis_cache_val_error,
)


class TestExceptions:
    """Тесты подготовленных ошибок"""

    def test_exc_401_not_val_cred(self):
        """Тест 401 ошибки на валидацию данных"""
        with pytest.raises(HTTPException) as exc_info:
            exc_401_not_val_cred("Bearer")

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
        assert exc_info.value.headers.get("WWW-Authentificate") == "Bearer"  # type: ignore

    def test_exc_link_404_not_found(self):
        """Тест 404 ошибки - ссылка не найдена"""
        with pytest.raises(HTTPException) as exc_info:
            exc_link_404_not_found()

        assert exc_info.value.status_code == 404
        assert "Link not found or not belong to user" in exc_info.value.detail

    def test_exc_link_410_gone(self):
        """Тест 410 ошибки - срок жизни ссылки закончилось"""
        with pytest.raises(HTTPException) as exc_info:
            exc_link_410_gone()

        assert exc_info.value.status_code == 410
        assert "Link expired" in exc_info.value.detail

    def test_exc_log_click_500_server_error(self):
        """Тест 500 ошибки - Не удалось залогировать клик (имеется в виду добавить в БД)"""
        with pytest.raises(HTTPException) as exc_info:
            exc_log_click_500_server_error()

        assert exc_info.value.status_code == 500
        assert "Failed to log click" in exc_info.value.detail

    def test_exc_short_code_existing(self):
        """Тест 409 ошибки - Ссылка {Код ссылки} уже используется"""
        with pytest.raises(HTTPException) as exc_info:
            exc_short_code_existing("abc123")

        assert exc_info.value.status_code == 409
        assert "Short code 'abc123' is already in use" in exc_info.value.detail

    def test_exc_400_expires_not_provided(self):
        """Тест 400 ошибки - о наличии срока жизни (неактуально)"""
        with pytest.raises(HTTPException) as exc_info:
            exc_400_expires_not_provided()

        assert exc_info.value.status_code == 400
        assert "Expires at must be provided" in exc_info.value.detail

    def test_exc_401_user_not_auth(self):
        """Тест 401 ошибки - Пользователь неавторизован"""
        with pytest.raises(HTTPException) as exc_info:
            exc_401_user_not_auth()

        assert exc_info.value.status_code == 401
        assert "Not Authentificated" in exc_info.value.detail

    def test_exc_403_user_forbidden_to_link(self):
        """Тест 403 ошибки - Ссылка не принадлежит пользователю"""
        with pytest.raises(HTTPException) as exc_info:
            exc_403_user_forbidden_to_link()

        assert exc_info.value.status_code == 403
        assert "Link does not belong to the current user" in exc_info.value.detail

    def test_exc_404_user_not_found(self):
        """Тест 404 ошибки - Пользователь не найден"""
        with pytest.raises(HTTPException) as exc_info:
            exc_404_user_not_found("user@example.com")

        assert exc_info.value.status_code == 404
        assert "User user@example.com not found" in exc_info.value.detail

    def test_exc_400_bad_request_patch(self):
        """Тест 400 ошибки - 1 поле при обновлении(изменение) данных должно быть"""
        with pytest.raises(HTTPException) as exc_info:
            exc_400_bad_request_patch()

        assert exc_info.value.status_code == 400
        assert "At least one field must be provided" in exc_info.value.detail

    def test_exc_400_bad_req_exp_link(self, mocker):
        """Тест 400 ошибки - Срок жизни ссылки должно быть между (мин.) и (макс.) дней"""
        # Мокаем настройки, чтобы тест был независим от реального конфига

        with patch("src.core.exceptions.settings") as mock_settings:
            mock_settings.ls.expire_in_days_min_length = 1
            mock_settings.ls.expire_in_days_max_length = 30

            with pytest.raises(HTTPException) as exc_info:
                exc_400_bad_req_exp_link()

            assert exc_info.value.status_code == 400
            assert "Link expiration must be between 1 and 30" in exc_info.value.detail

    def test_exc_403_admin_forbidden(self):
        """Тест 403 ошибки - Пользователь должен быть админом"""
        with pytest.raises(HTTPException) as exc_info:
            exc_403_admin_forbidden()

        assert exc_info.value.status_code == 403
        assert (
            "Not enough permissions to perform this action. The administrator role is required"
            in exc_info.value.detail
        )

    def test_exc_redis_cache_val_error(self):
        """
        Тест Redis ошибки - Проблема с валидацией данных.
        Эта функция не выбрасывает исключение, а возвращает строку
        """

        result = exc_redis_cache_val_error("Error Validation")
        assert "ERROR:" in result
        assert "[ID-13]" in result
        assert "Redis cache validation error: Error Validation" in result
