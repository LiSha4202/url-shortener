from datetime import datetime, timezone

from fastapi import Depends, Request, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse

from core.database.engine import db_engine
from core.exceptions import (
    exc_link_404_not_found,
    exc_link_410_gone,
    exc_log_click_500_server_error,
)
from crud.click_crud import create_click_log
from crud.link_crud import get_link_by_code, increment_click_count

router = APIRouter(tags=["redirects"])


@router.get("/{short_code}", include_in_schema=False)
async def redirect_to_original(
    request: Request,
    short_code: str,
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Редирект по короткой ссылке + обновление статистики"""

    db_link = await get_link_by_code(session=session, code=str(short_code))
    if not db_link:
        return exc_link_404_not_found()

    # Провека на истёкшие ссылки
    if (db_link.expires_at) and db_link.expires_at < datetime.now(timezone.utc):
        return exc_link_410_gone()

    # --- User Agent ---

    ip_address = request.client.host if request.client else None
    user_agent_string = request.headers.get("user-agent")

    device_type = None
    browser_name = None

    if user_agent_string:
        ua_object = parse(user_agent_string)
        device_type = ua_object.device.family
        browser_name = ua_object.browser.family

    await create_click_log(
        session=session,
        link_id=db_link.id,
        device_type=device_type,
        browser=browser_name,
        ip_address=ip_address,
    )

    if not create_click_log:
        raise exc_log_click_500_server_error()

    # Увеличение счётчика кликов
    if not increment_click_count(session, short_code):
        return exc_log_click_500_server_error()

    return RedirectResponse(url=db_link.original_url)
