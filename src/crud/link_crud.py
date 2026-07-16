from datetime import datetime, date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.links_model import Link
from core.schemas.link_schema import LinkCreate


async def create_link(session: AsyncSession, link_data: LinkCreate):
    """Создание новой ссылки"""

    link_dict = link_data.model_dump()
    link_dict["original_url"] = str(link_dict["original_url"])

    new_link = Link(**link_dict)
    session.add(new_link)
    await session.commit()
    return new_link


async def get_link_by_code(session: AsyncSession, code: str) -> Link | None:
    """Получение ссылки по его короткому коду"""

    return await session.get(Link, code)


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
