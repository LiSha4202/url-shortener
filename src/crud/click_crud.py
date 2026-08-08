from typing import Optional
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.clicks_model import ClickLog
from models.links_model import Link

from core.schemas.click_schema import ClickLogResponse
from core.redis_client import redis_client
from core.exceptions import exc_redis_cache_val_error


async def create_click_log(
    session: AsyncSession,
    link_id: int,
    device_type: Optional[str] = None,
    browser: Optional[str] = None,
    ip_address: Optional[str] = None,
):
    """Создание лога о клике"""
    click_log = ClickLog(
        link_id=link_id,
        device_type=device_type,
        browser=browser,
        ip_address=ip_address,
    )

    session.add(click_log)
    await session.commit()
    await session.refresh(click_log)

    cache_key = f"click_history:{click_log.link_id}"
    try:
        await redis_client.delete(cache_key)
    except Exception as e:
        print(exc_redis_cache_val_error(e))

    return click_log


async def get_link_detail_click_history(
    session: AsyncSession,
    short_code: str,
    limit: int = 100,
) -> list[ClickLogResponse]:
    """Получение подробной истории кликов для конкретной ссылки"""

    cache_key = f"click_history:{short_code}"

    # Проверяем кэш
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        data_list = json.loads(cached_data)  # Десериализация данных из Redis
        return [ClickLogResponse(**item) for item in data_list]

    link_stmt = select(Link.id).where(Link.short_code == short_code)
    result = await session.execute(link_stmt)
    link_id = result.scalar_one_or_none()

    if not link_id:
        return []

    stmt = (
        select(ClickLog)
        .where(ClickLog.link_id == link_id)
        .order_by(ClickLog.created_at.desc())
        .limit(limit)
    )

    result = await session.execute(stmt)
    logs = result.scalars().all()

    response = [ClickLogResponse.model_validate(log) for log in logs]

    try:
        serialized_data = json.dumps([log for log in logs])  # Сериализуем данные в JSON
        await redis_client.setex(cache_key, 300, serialized_data)
    except Exception as e:
        print(f"Redis error: {e}")

    return response
