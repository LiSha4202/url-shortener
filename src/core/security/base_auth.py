from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import db_engine
from core.exceptions import exc_401_not_val_cred
from core.security.jwt_auth import decode_jwt_token

from models.users_model import User

from crud.user_crud import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
) -> Optional[User]:
    """Проверка JWT-токена"""
    if not token:
        return None

    try:
        payload = decode_jwt_token(token)

        if payload is None:
            return None

        email: str = payload.get("sub")  # type: ignore
        if email is None:
            return None

        user = await get_user_by_email(session, email)
        if user is None:
            return None

        return user
    except HTTPException as e:
        return None
