from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import db_engine
from core.schemas.link_schema import (
    LinkCreate,
    LinkResponse,
    LinkStats,
    LinkStatsAll,
    LinkStatsTop,
    LinksMe,
    LinkUpdate,
)
from core.exceptions import (
    exc_link_404_not_found,
    exc_link_410_gone,
    exc_log_click_500_server_error,
    exc_400_expires_not_provided,
    exc_401_user_not_auth,
    exc_403_user_forbidden_to_link,
)
from core.security.base_auth import get_current_user

from models.users_model import User

from crud.link_crud import (
    create_link,
    get_link_by_code,
    increment_click_count,
    get_links_stats_all,
    get_link_stats_top,
    get_link_sorted_by_user_id,
    update_link,
    delete_link,
)

router = APIRouter(prefix="/links", tags=["links"])


@router.post(
    "/create", response_model=LinkResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_link(
    link_in: LinkCreate,
    session: AsyncSession = Depends(
        db_engine.scoped_session_dependency,
    ),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Создание короткой ссылки"""

    db_link = await create_link(
        session,
        link_in,
        user_id=current_user.id if current_user else None,
    )

    return LinkResponse(
        short_code=db_link.short_code,
        original_url=str(db_link.original_url),
        created_at=db_link.created_at,
        expires_at=db_link.expires_at,
    )


@router.patch("/{short_code}/update", response_model=LinkResponse)
async def update_link_route(
    short_code: str,
    link_update: LinkUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Обновление срока жизни ссылки"""

    if not current_user:
        raise exc_401_user_not_auth()

    if not link_update.expires_at:
        raise exc_400_expires_not_provided()

    db_link = await update_link(
        session,
        short_code=short_code,
        link_update=link_update,
        user_id=current_user.id,
    )

    if not db_link:
        raise exc_403_user_forbidden_to_link()

    return LinkResponse(
        short_code=db_link.short_code,
        original_url=str(db_link.original_url),
        created_at=db_link.created_at,
        expires_at=db_link.expires_at,
    )


@router.delete(
    "/{short_code}/delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_link_route(
    short_code: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Удаление ссылки"""

    if not current_user:
        raise exc_401_user_not_auth()

    deleted = await delete_link(
        session,
        short_code=short_code,
        user_id=current_user.id,
    )

    if not deleted:
        raise exc_link_404_not_found()

    return None


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


@router.get("/stats/all", response_model=LinkStatsAll)
async def get_all_links_stats(
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Получение общей статистики по всем ссылкам"""
    return await get_links_stats_all(session)


@router.get("/stats/top", response_model=list[LinkStatsTop])
async def get_top_links_stats(
    limit: int = 10,
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Получение топ популярных ссылок"""

    return await get_link_stats_top(session, limit=limit)


@router.get("/{}/my_links", response_model=list[LinksMe])
async def get_links_by_user_id(
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(
        db_engine.scoped_session_dependency,
    ),
):
    """Получение ссылок пользователя по его ID"""

    return await get_link_sorted_by_user_id(
        session,
        user_id=current_user.id if current_user else None,
    )
