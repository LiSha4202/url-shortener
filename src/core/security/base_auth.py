from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import db_engine
from core.exceptions import exc_401_not_val_cred
from core.security.jwt_auth import decode_jwt_token

from crud.user_crud import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Проверка JWT-токена"""

    payload = decode_jwt_token(token)

    if payload is None:
        return exc_401_not_val_cred(header_type="Bearer")

    email: str = payload.get("sub")  # type: ignore
    if email is None:
        return exc_401_not_val_cred(header_type="Bearer")

    user = await get_user_by_email(session, email)
    if user is None:
        return exc_401_not_val_cred(header_type="Bearer")

    return user
