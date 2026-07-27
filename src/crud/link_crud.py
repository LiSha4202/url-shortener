from datetime import datetime, date, timedelta

from typing import Optional

from sqlalchemy import select, func, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.links_model import Link

from core.config import settings
from core.exceptions import exc_short_code_existing
from core.schemas.link_schema import (
    LinkCreate,
    LinkStatsAll,
    LinkStatsTop,
    LinksMe,
    LinkUpdate,
)

from utils.base62 import generaste_short_code


async def create_link(
    session: AsyncSession, link_data: LinkCreate, user_id: Optional[int] = None
):
    """Создание новой ссылки"""
    link_dict = link_data.model_dump()  # Создаем словарь из модели
    link_dict["original_url"] = str(  # И модифицируем его
        link_dict["original_url"]
    )  # Переводим тип данных с HTTPUrl на строку для корректной работы sqlalchemy

    if not link_dict.get("short_code"):
        while True:
            short_code = generaste_short_code(length=settings.ls.shortcode_max_length)
            # Проверяем, что код не занят
            existings = await get_link_by_code(session, short_code)
            if not existings:
                link_dict["short_code"] = short_code
                break
    else:
        # Проверяем не занят ли кастомны код
        existing = await get_link_by_code(session, link_dict["short_code"])
        if existing:
            raise exc_short_code_existing(shortcode=link_dict["short_code"])

    if link_data.expires_at:
        link_dict["expires_at"] = datetime.utcnow() + timedelta(
            days=link_data.expires_at  # type: ignore
        )  # Устанавливаем срок жизни ссылки
    else:
        link_dict["expires_at"] = None  # По умолчанию - бессрочная ссылка

    # Явно задаем short_url
    link_dict["short_url"] = (
        f"http://{settings.run.host}:{settings.run.port}/{link_dict['short_code']}"
    )

    # Добавляем данные о пользователе, если они указаны
    if user_id is not None:
        link_dict["user_id"] = user_id

    new_link = Link(**link_dict)
    session.add(new_link)
    await session.commit()

    return new_link


async def get_link_by_code(session: AsyncSession, code: str) -> Link | None:
    """Получение ссылки по его короткому коду"""

    stmt = select(Link).where(Link.short_code == code)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_links(session: AsyncSession) -> list[Link]:
    """Получение всех ссылок"""

    stmt = select(Link).order_by(Link.id)
    result = await session.execute(stmt)
    link = result.scalars().all()
    return list(link)


async def increment_click_count(session: AsyncSession, short_code: str) -> bool:
    """Увеличение количества кликов по ссылке"""

    short_code_db_link = await get_link_by_code(session, short_code)
    if not short_code_db_link:
        return False

    # Увеличиваем счётчик перехода по ссылке
    short_code_db_link.clicks_count += 1
    now = datetime.utcnow()  # Записываем текущее время

    if not short_code_db_link.first_click:  # Если это первое нажатие на ссылку...
        short_code_db_link.first_click = now  # ...то записываем время первого клика
    short_code_db_link.last_click = now  # Обновляем последнее время клика

    # Теперь записываем в статистику clicks_by_day
    today = date.today().isoformat()  # получаем сегодняшнюю дату
    day_data = (
        short_code_db_link.clicks_by_day or {}
    )  # Получение данных за день или создание нового словаря
    day_data[today] = (
        day_data.get(today, 0) + 1
    )  # Увеличиваем количество переходов сегодняшенй даты на 1

    await session.commit()
    return True


async def get_links_stats_all(session: AsyncSession) -> LinkStatsAll:
    """Получение общей статистики по всем ссылкам"""

    now = datetime.utcnow()

    total_clicks = await session.execute(
        select(func.sum(Link.clicks_count)).select_from(Link)
    )
    total_clicks_sum = total_clicks.scalar_one()

    total_links = await session.execute(select(func.count()).select_from(Link))
    total_links_count = total_links.scalar_one()

    active_links = await session.execute(
        select(func.count()).where(
            Link.expires_at.is_(None) | (Link.expires_at > now),
        )
    )
    active_links_count = active_links.scalar_one()

    expired_links_count = total_links_count - active_links_count

    return LinkStatsAll(
        total_clicks=total_clicks_sum,
        total_links=total_links_count,
        active_links=active_links_count,
        expired_links=expired_links_count,
    )


async def get_link_stats_top(
    session: AsyncSession,
    limit: int = 10,
) -> list[LinkStatsTop]:
    """Получение топа популярных ссылок"""

    stmt = (
        select(Link)
        .where(Link.clicks_count == 0)
        .order_by(Link.clicks_count.desc())
        .limit(limit)
    )

    result = await session.execute(stmt)
    links = result.scalars().all()

    return [
        LinkStatsTop(
            short_code=link.short_code,
            original_url=link.original_url,
            click_count=link.clicks_count,
            created_at=link.created_at,
        )
        for link in links
    ]


async def get_link_sorted_by_user_id(
    session: AsyncSession,
    user_id: Optional[int],
) -> list[LinksMe]:
    """Получение данных о ссылках по user_id"""

    if user_id is None:
        return []

    stmt = select(Link).where(Link.user_id == user_id)
    result = await session.execute(stmt)
    links = result.scalars().all()

    return [
        LinksMe(
            short_code=link.short_code,
            original_url=link.original_url,
            user_id=link.user_id,
            created_at=link.created_at,
            expires_at=link.expires_at,
        )
        for link in links
    ]


async def update_link(
    session: AsyncSession,
    short_code: str,
    link_update: LinkUpdate,
    user_id: int,
) -> Link | None:
    """Обновление ссылки по short_code"""

    stmt = update(Link).where(Link.short_code == short_code)

    values = {}
    if link_update.original_url is not None:
        values["original_url"] = str(link_update.original_url)
    if link_update.expires_at is not None:
        values["expires_at"] = datetime.utcnow() + timedelta(
            days=link_update.expires_at
        )

    if not values:
        return None

    stmt = stmt.values(**values).where(Link.user_id == user_id)

    result = await session.execute(stmt)
    await session.commit()

    updated_link = await get_link_by_code(session, short_code)
    if not updated_link or updated_link.user_id != user_id:
        return None

    return updated_link


async def delete_link(
    session: AsyncSession,
    short_code: str,
    user_id: int,
) -> bool:
    """Удаление ссылки по short_code"""

    link = await get_link_by_code(session, short_code)

    if not link:
        return False

    if link.user_id != user_id:
        return False

    stmt = delete(Link).where(
        and_(Link.short_code == short_code, Link.user_id == user_id)
    )

    await session.execute(stmt)
    await session.commit()

    return True
