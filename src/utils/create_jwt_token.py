from datetime import timedelta, datetime, timezone
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
    to_encode = data.copy()  # копируем словарь
    if expires_delta:  # если есть дельта времени, то добавляем ее к текущему моменту
        expire = datetime.now(timezone.utc) + expires_delta
    else:  # иначе ставим время жизни токенов в зависимости от переданного числа
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_time)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt.jwt_secret_key, algorithm=jwt_algorithm)


def create_refresh_jwt_token(
    data: dict,
    expires_time: int,
    jwt_algorithm: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Функция создания Refresh-токена"""
    # Работает таким же способом, как и функция выше, разница в timedelta(Здесь days, там minutes)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=expires_time)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt.jwt_secret_key, algorithm=jwt_algorithm)
