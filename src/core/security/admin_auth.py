from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import db_engine
from core.security.base_auth import get_current_user
from core.exceptions import exc_403_admin_forbidden

from models.users_model import User


async def get_current_admin_user(
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Зависимость, которая проверяет является ли пользователь администратором.
    Если нет - возвращает ошибку 403 Forbidden.
    """
    if not current_user.is_admin:
        raise exc_403_admin_forbidden()
    return current_user
