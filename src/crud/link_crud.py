from datetime import datetime, date, timedelta

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.links_model import Link

from core.config import settings
from core.schemas.link_schema import LinkCreate

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
            short_code = generaste_short_code(length=8)
            # Проверяем, что код не занят
            existings = await get_link_by_code(session, short_code)
            if not existings:
                link_dict["short_code"] = short_code
                break
    else:
        # Проверяем не занят ли кастомны код
        existing = await get_link_by_code(session, link_dict["short_code"])
        if existing:
            raise ValueError(
                f"Short code '{link_dict['short_code']}' is already in use"
            )

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
