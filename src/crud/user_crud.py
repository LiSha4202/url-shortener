from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users_model import User  # SQLAlchemy модель
from src.core.schemas.user_schema import UserCreate  # Pydantic схема


async def create_user(session: AsyncSession, user: UserCreate):
    """Создание нового пользователя"""

    new_user = User(**user.model_dump())
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user_by_id(session: AsyncSession, id: int) -> User | None:
    """Нахождение пользователя по его ID"""

    return await session.get(User, id)


async def get_all_users(session: AsyncSession) -> list[User]:
    """Получение всех пользователей"""

    stmt = select(User).order_by(User.id)
    result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)
