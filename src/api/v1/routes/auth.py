from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import db_engine
from core.schemas.user_schema import UserCreate
from core.security.base_auth import get_current_user

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
async def login():
    """TODO: Реализовать JWT-Аутентификацию"""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login not implemented yet",
    )


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
