import pytest

from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Generator

from crud.link_crud import (
    create_link,
    get_link_by_code,
    get_all_links,
    increment_click_count,
    get_links_stats_all,
    get_link_stats_top,
    get_link_sorted_by_user_id,
    update_link,
    delete_link,
)
from core.schemas.link_schema import LinkCreate, LinkUpdate, LinkStatsAll
from models.links_model import Link


class TestLinkCRUD:

    async def test_create_link_default_code(self, db_session, mock_link_crud_settings):
        """Тест создания ссылки с автоматическим генерированием кода"""
        link_data = LinkCreate(original_url="https://example.com/")  # type: ignore

        new_link = await create_link(db_session, link_data)

        assert new_link is not None
        assert new_link.short_code is not None
        assert (
            len(new_link.short_code) <= mock_link_crud_settings.ls.short_code_max_length
        )
        assert new_link.original_url == "https://example.com/"
        assert new_link.created_at is not None
        assert new_link.expires_at is None  # По умолчанию не истекает

    async def test_create_link_custom_code(self, db_session, mock_link_crud_settings):
        """Тест создания ссылки с кастомным кодом"""
        link_data = LinkCreate(
            original_url="https://example.com/",  # type: ignore
            short_code="customcode",
        )

        new_link = await create_link(db_session, link_data)

        assert new_link.short_code == "customcode"
        assert new_link.original_url == "https://example.com/"

    async def test_create_link_expires_at(self, db_session, mock_link_crud_settings):
        """Тест создания ссылки с истекающим сроком"""
        link_data = LinkCreate(  # type: ignore
            original_url="https://google.com/",
            expires_at=10,
        )

        new_link = await create_link(db_session, link_data)

        assert new_link.expires_at is not None
        # Проверяеи, что дата установлена примерно на 10 дней
        # (с учетом времени выполнения теста, точное сравнение сложно вычислить, проверяем наличие)
        assert new_link.expires_at > datetime.now(timezone.utc)

    async def test_create_link_existing_custom_code(
        self, db_session, mock_link_crud_settings
    ):
        """Тест создания ссылки с уже занятым кастомным кодом"""
        # Создаем 1 ссылку
        await create_link(
            db_session,
            LinkCreate(
                original_url="https://first.com/",  # type: ignore
                short_code="unique_code",
            ),
        )
        from core.exceptions import exc_short_code_existing

        with pytest.raises(HTTPException):  # type: ignore
            await create_link(
                db_session,
                LinkCreate(
                    original_url="https://first.com/",  # type: ignore
                    short_code="unique_code",
                ),
            )

    async def test_get_link_by_code(self, db_session, mock_link_crud_settings):
        """Тест получения ссылки по коду"""
        link_data = LinkCreate(original_url="https://example.com/")  # type: ignore
        created_link = await create_link(db_session, link_data)

        retrieved_link = await get_link_by_code(db_session, created_link.short_code)

        assert retrieved_link is not None
        assert retrieved_link.short_code == created_link.short_code
        assert retrieved_link.original_url == created_link.original_url

    async def test_get_link_by_code_not_found(
        self, db_session, mock_link_crud_settings
    ):
        """Тест получения несуществующей ссылки"""
        result = await get_link_by_code(db_session, "nonexistened")
        assert result is None

    async def test_get_all_links(self, db_session):
        """Тест получения всех ссылок"""
        for i in range(3):
            await create_link(
                db_session, LinkCreate(original_url=f"https://example{i}.com/")  # type: ignore
            )
        links = await get_all_links(db_session)

        assert len(links) == 3
        assert all(isinstance(l, Link) for l in links)

    async def test_increment_click_count(self, db_session, mock_link_crud_settings):
        """Тест инкремента счётчика кликов"""
        link_data = LinkCreate(original_url="https://example.com/")  # type: ignore
        link = await create_link(db_session, link_data)
        code = link.short_code

        # Сбрасываем счётчик для чистоты теста
        link.clicks_count = 0
        link.first_click = None  # type: ignore
        link.last_click = None  # type: ignore
        link.clicks_by_day = {}
        await db_session.flush()

        result = await increment_click_count(db_session, code)

        assert result is True

        # Проверяем обновление данных
        updated_link = await get_link_by_code(db_session, code)
        assert updated_link is not None
        assert updated_link.clicks_count == 1
        assert updated_link.first_click is not None
        assert updated_link.last_click is not None

    async def test_increment_click_count_not_found(
        self,
        db_session,
        mock_link_crud_settings,
    ):
        """Тест инкремента для несуществующей ссылки"""
        result = await increment_click_count(db_session, "noexist")
        assert result is False

    async def test_update_link(self, db_session, mock_link_crud_settings, create_user):
        """Тест обновления ссылки"""
        link_data = LinkCreate(original_url="https://example.com/")  # type: ignore
        link = await create_link(db_session, link_data, create_user.id)

        update_data = LinkUpdate(original_url="https://new.com/")  # type: ignore

        updated_link = await update_link(
            db_session, link.short_code, update_data, create_user.id
        )

        assert updated_link is not None
        assert updated_link.original_url == "https://new.com/"

    async def test_update_link_not_found(self, db_session):
        """Тест обновления несуществующей ссылки"""
        result = await update_link(
            db_session,
            "noexist",
            LinkUpdate(original_url="https://new.com"),  # type: ignore
            1,
        )  # type: ignore
        assert result is None

    async def test_delete_link(self, db_session, mock_link_crud_settings, create_user):
        """Тест удаления ссылки"""
        link_data = LinkCreate(original_url="https://example.com/")  # type: ignore
        link = await create_link(db_session, link_data, create_user.id)

        result = await delete_link(db_session, link.short_code, create_user.id)

        assert result == True

        # Проверяем что ссылки больше нет
        retrieved = await get_link_by_code(db_session, link.short_code)
        assert retrieved is None

    async def test_delete_link_not_found(self, db_session, mock_link_crud_settings):
        """Тест удаления несуществующей ссылки"""
        result = await delete_link(db_session, "noexist", 1)
        assert result is False

    async def test_get_links_stats_all(self, db_session, mock_link_crud_settings):
        """Тест получения глобальной статистики"""
        for i in range(5):
            await create_link(
                db_session, LinkCreate(original_url=f"https://example{i}.com/")  # type: ignore
            )
        stats = await get_links_stats_all(db_session)

        assert isinstance(stats, LinkStatsAll)
        assert stats.total_links == 5
        assert stats.total_clicks == 0
        assert stats.active_links == 5
        assert stats.expired_links == 0

    async def test_get_link_stats_top(self, db_session, mock_link_crud_settings):
        """Тест получения топа популярных ссылок"""

        link1 = await create_link(
            db_session, LinkCreate(original_url="https://top1.com/")  # type: ignore
        )

        link2 = await create_link(
            db_session, LinkCreate(original_url="https://top2.com/")  # type: ignore
        )

        await increment_click_count(db_session, link1.short_code)
        await increment_click_count(db_session, link1.short_code)
        await increment_click_count(db_session, link1.short_code)

        await increment_click_count(db_session, link2.short_code)

        top_links = await get_link_stats_top(db_session, limit=2)

        assert len(top_links) == 2
        assert (
            top_links[0].short_code == link1.short_code
        )  # У первой ссылки больше кликов
        assert top_links[1].short_code == link2.short_code
