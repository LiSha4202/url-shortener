from datetime import timedelta

from fastapi import Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings

from core.database.engine import db_engine
from core.schemas.user_schema import UserCreate, UserResponse

from core.security.base_auth import get_current_user
from core.security.jwt_auth import (
    authentificate_user,
    create_access_token,
    create_refresh_token,
)

from models.users_model import User

from crud.user_crud import create_user

router = APIRouter(prefix="/auth", tags=["authentification"])


@router.post(
    "/register", response_model=UserCreate, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Регистрация нового пользователя"""

    return await create_user(session, user_in)


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Аутентификация и получение JWT токенов"""
    user = await authentificate_user(session, form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=settings.jwt.access_token_expire_minutes)
    refresh_token_expires = timedelta(days=settings.jwt.refresh_token_expire_days)

    access_token = create_access_token(
        data={"sub": user.email},  # type: ignore
        expires_delta=access_token_expires,
    )

    refresh_token = create_refresh_token(
        data={"sub": user.email},  # type: ignore
        expires_delta=refresh_token_expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
