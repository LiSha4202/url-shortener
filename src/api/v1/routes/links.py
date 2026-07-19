from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import db_engine
from core.schemas.link_schema import LinkCreate, LinkResponse, LinkStats
from core.config import settings
from core.exceptions import (
    exc_link_404_not_found,
    exc_link_410_gone,
    exc_log_click_500_server_error,
)

from crud.link_crud import create_link, get_link_by_code, increment_click_count
from models.links_model import Link

router = APIRouter(prefix="/links", tags=["links"])


@router.post(
    "/create", response_model=LinkResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_link(
    link_in: LinkCreate,
    session: AsyncSession = Depends(
        db_engine.scoped_session_dependency,
    ),
):
    """Создание короткой ссылки"""

    db_link = await create_link(session, link_in)
    rt_short_url = (
        f"http://{settings.run.host}:{settings.run.port}/{db_link.short_code}"
    )

    return LinkResponse(
        short_code=db_link.short_code,
        short_url=rt_short_url,
        original_url=str(db_link.original_url),
        created_at=db_link.created_at,
        expires_at=db_link.expires_at,
    )


@router.get("/{short_code}", include_in_schema=False)
async def redirect_to_original(
    short_code: str,
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Редирект по короткой ссылке + обновление статистики"""

    db_link = await get_link_by_code(session=session, code=str(short_code))
    if not db_link:
        return exc_link_404_not_found()

    # Провека на истёкшие ссылки
    if (db_link.expires_at) and db_link.expires_at < datetime.utcnow():
        return exc_link_410_gone()

    # Увеличение счётчика кликов
    if not increment_click_count(session, short_code):
        return exc_log_click_500_server_error()

    return RedirectResponse(url=db_link.original_url)


@router.get("/{short_code}/stats", response_model=LinkStats)
async def get_link_stats(
    short_code=str,
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Получение статистики по ссылке"""

    db_link = await get_link_by_code(session, str(short_code))
    if not db_link:
        return exc_link_404_not_found()

    return LinkStats(
        short_code=db_link.short_code,
        clicks_count=db_link.clicks_count,
        first_click=db_link.first_click,
        last_click=db_link.last_click,
        clicks_by_day=db_link.clicks_by_day,
    )
