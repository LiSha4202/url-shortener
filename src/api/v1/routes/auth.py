from datetime import timedelta

from fastapi import Depends, APIRouter, status, Response, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings

from core.database.engine import db_engine
from core.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserPatchResponse,
)

from core.security.base_auth import get_current_user
from core.security.jwt_auth import (
    authentificate_user,
    create_access_token,
    create_refresh_token,
)
from core.exceptions import (
    exc_401_user_not_auth,
    exc_404_user_not_found,
    exc_400_bad_request_patch,
)

from models.users_model import User

from crud.user_crud import create_user, update_user, delete_user

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
    response: Response = Response(),
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

    response.set_cookie(
        key=settings.sc.key,
        value=f"Bearer {access_token}",
        httponly=settings.sc.httponly,
        samesite=settings.sc.samesite,  # type: ignore
        secure=settings.sc.secure,
        max_age=settings.sc.max_age,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout: очистка токена"""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.patch("/update", response_model=UserPatchResponse)
async def patch_user(
    user_update: UserUpdate = Body(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Частичное обновление данных пользователя (Роут)"""

    if not current_user:
        raise exc_401_user_not_auth()

    if not any(
        [
            user_update.username,
            user_update.email,
            user_update.password,
        ]
    ):
        raise exc_400_bad_request_patch()

    db_user = await update_user(
        session,
        user_update=user_update,
        user_id=current_user.id,
    )

    if not db_user:
        raise exc_401_user_not_auth()

    return db_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_engine.scoped_session_dependency),
):
    """Удаление пользователя"""

    if not current_user:
        return exc_401_user_not_auth()

    user_delete = await delete_user(
        session,
        user_id=current_user.id,
    )

    if not user_delete:
        raise exc_404_user_not_found(current_user.email)

    return None
