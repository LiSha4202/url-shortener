from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.engine import db_engine
from crud.user_crud import create_user, get_user_by_id
from core.schemas.user_schema import UserCreate
from models.users_model import User

router = APIRouter(prefix="/auth", tags=["authentification"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(session: AsyncSession, user_in: UserCreate):
    """Регистрация нового пользователя"""

    return await create_user(session, user_in)


@router.post("/login")
async def login():
    """TODO: Реализовать JWT-Аутентификацию"""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login not implemented yet",
    )
