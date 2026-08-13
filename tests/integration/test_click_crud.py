import pytest
from crud.click_crud import create_click_log, get_link_detail_click_history


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
