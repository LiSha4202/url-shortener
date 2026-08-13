import pytest
import json
import sys

from unittest.mock import AsyncMock, MagicMock, patch

from crud.click_crud import create_click_log, get_link_detail_click_history
from core.schemas.click_schema import ClickLogResponse


@pytest.mark.asyncio
class TestClickCrud:

    async def test_create_click_log_success(self, db_session, created_link):
        """Тест создает новый лог клика и проверяет, что он корректно сохранён в БД"""

        # Инициализация тестовых данных
        link_id = created_link.id
        device_type = "Desktop"
        browser = "Chrome"
        ip_address = "192.168.1.1"

        # Вызываем тестируемую фунцкию
        log = await create_click_log(
            session=db_session,
            link_id=link_id,
            device_type=device_type,
            browser=browser,
            ip_address=ip_address,
        )

        # Проверяем результат
        assert log is not None

        # Проверим, что все поля заполнены корректно
        assert log.link_id == link_id
        assert log.device_type == device_type
        assert log.browser == browser
        assert log.ip_address == ip_address

        # Проверяем, что запись реально создана в БД
        assert log.id is not None
        assert log.id > 0

    async def test_get_link_detail_click_history(self, db_session, created_link):
        """Тест проверяет получение истории кликов из БД"""

        # Подготовка данных в БД
        # убедимся, что created_link имеет корректный short_code
        short_code = created_link.shortcode
        link_id = created_link.id

        # Добавляем один клик лога
        log = await create_click_log(
            session=db_session,
            link_id=link_id,
            device_type="Desktop",
            browser="Chrome",
            ip_address="192.168.1.1",
        )

        # Вызов функции
        result = await get_link_detail_click_history(
            session=db_session,
            short_code=short_code,
            limit=100,
        )

        # Проверки
        assert len(result) == 1
        assert isinstance(result[0], ClickLogResponse)

        # Проверяем данные
        item = result[0]
        assert item.id == log.id
        assert item.device_type == "Desktop"
        assert item.browser == "Chrome"
        assert str(item.ip_address) == "192.168.1.1"

    async def test_get_link_detail_click_history_link_not_found(self, db_session):
        """Тест проверки поведения, когда ссылка с таким short_code не найдена"""

        result = await get_link_detail_click_history(
            session=db_session, short_code="nonexistent_link", limit=100
        )

        assert result == []
