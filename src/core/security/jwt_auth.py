from datetime import timedelta, datetime
from typing import Optional

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import get_401_exception

from core.security.create_jwt_token import create_jwt_token

from crud.hash_password import verify_password
from crud.user_crud import get_user_by_email
from models.users_model import User

# Настройки JWT
ALGORITHM = settings.jwt.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRES_DAYS = settings.jwt.refresh_token_expire_days


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
):
    """Создание Access токена"""
    return create_jwt_token(
        data=data,
        expires_time=expires_minutes,
        jwt_algorithm=ALGORITHM,
        expires_delta=expires_delta,
    )


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    expires_days=REFRESH_TOKEN_EXPIRES_DAYS,
):
    """Создание Refresh токена"""

    return create_jwt_token(
        data=data,
        expires_time=expires_days,
        jwt_algorithm=ALGORITHM,
        expires_delta=expires_delta,
    )


async def authentificate_user(
    session: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Проверка данных пользователя"""

    user = await get_user_by_email(session, email)
    if not user:
        get_401_exception(header_type="Bearer")
    if not verify_password(password, user.password):  # type: ignore
        get_401_exception(header_type="Bearer")

    return user
