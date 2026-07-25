from datetime import timedelta
from typing import Optional

from jose import jwt, exceptions
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import exc_401_not_val_cred

from utils.create_jwt_token import (
    create_access_jwt_token,
    create_refresh_jwt_token,
)

from utils.hash_password import verify_password
from crud.user_crud import get_user_by_email
from models.users_model import User


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    expires_minutes=settings.jwt.access_token_expire_minutes,
):
    """Создание Access токена"""
    return create_access_jwt_token(
        data=data,
        expires_time=expires_minutes,
        jwt_algorithm=settings.jwt.algorithm,
        expires_delta=expires_delta,
    )


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    expires_days=settings.jwt.refresh_token_expire_days,
):
    """Создание Refresh токена"""

    return create_refresh_jwt_token(
        data=data,
        expires_time=expires_days,
        jwt_algorithm=settings.jwt.algorithm,
        expires_delta=expires_delta,
    )


async def authentificate_user(
    session: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Проверка данных пользователя"""

    user = await get_user_by_email(session, email)
    if not user:
        raise exc_401_not_val_cred(header_type="Bearer")
    if not verify_password(password, user.password):  # type: ignore
        raise exc_401_not_val_cred(header_type="Bearer")

    return user


def decode_jwt_token(token: str):
    """Декодирование JWT-токена"""
    if token is None:
        return None
    try:
        return jwt.decode(token, key=settings.jwt.jwt_secret_key)
    except exceptions:
        print("Error JWT")
        return None
