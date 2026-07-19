from datetime import timedelta, datetime
from typing import Optional

from jose import jwt

from core.config import settings


def create_access_jwt_token(
    data: dict,
    expires_time: int,
    jwt_algorithm: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Функция создания Access-токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=expires_time)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt.jwt_secret_key, algorithm=jwt_algorithm)


def create_refresh_jwt_token(
    data: dict,
    expires_time: int,
    jwt_algorithm: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Функция создания Refresh-токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=expires_time)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt.jwt_secret_key, algorithm=jwt_algorithm)
