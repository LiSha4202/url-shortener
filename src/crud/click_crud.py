from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.clicks_model import ClickLog
from models.links_model import Link

from core.schemas.click_schema import ClickLogResponse


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
    return click_log


async def get_link_click_history(
    session: AsyncSession,
    short_code: str,
    limit: int = 100,
) -> list[ClickLogResponse]:
    """Получение подробной истории кликов для конкретной ссылки"""

    link_stmt = select(Link).where(Link.short_code == short_code)
    result = await session.execute(link_stmt)
    link_id = result.scalar_one_or_none()

    if not link_id:
        return []

    stmt = (
        select(ClickLog)
        .where(ClickLog.id == link_id)
        .order_by(ClickLog.created_at.desc())
        .limit(limit)
    )

    result = await session.execute(stmt)
    logs = result.scalars().all()

    return [ClickLogResponse.model_validate(log) for log in logs]
