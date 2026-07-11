from datetime import datetime

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from core.config import settings


class UserModel(BaseModel):
    username: str = Field(
        ...,
        min_length=settings.us.username_min_length,
        max_length=settings.us.username_max_length,
        description="Имя пользователя (Уникальное)",
    )
    email: EmailStr = Field(
        ...,
        description="Почта пользователя",
    )
    created_at: datetime = Field(
        ...,
        description="Время создания аккаунта пользователя",
    )


class UserCreate(UserModel):
    password: str = Field(
        ...,
        min_length=settings.us.password_min_length,
        description="Пароль (Минимум 8 символов)",
    )


class UserResponse(UserModel):
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True  # В Pydantic V2: вместо orm_mode=True
        # Модель может быть создана из ORM-объекта (Из user_model для БД)


class UserUpdate(UserModel):
    username: Optional[str] = Field(
        None,
        description="Новое имя пользователя",
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Новая почта пользователя",
    )
    password: Optional[str] = Field(
        None,
        description="Новый пароль",
    )
