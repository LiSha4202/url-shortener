from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import db_engine
from core.exceptions import get_401_exception

from crud.hash_password import verify_password
from crud.user_crud import get_user_by_email

security = HTTPBasic()


async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Проверка Basic Auth (Login + password)"""
    user = await get_user_by_email(session, credentials.username)

    if not user:
        get_401_exception()

    if not verify_password(credentials.password, user.password):  # type: ignore
        get_401_exception()

    return user
