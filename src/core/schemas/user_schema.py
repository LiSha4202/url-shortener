from datetime import datetime

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserModel(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
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
        min_length=8,
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
