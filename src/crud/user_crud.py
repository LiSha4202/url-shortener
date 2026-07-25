from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.users_model import User  # SQLAlchemy модель
from core.schemas.user_schema import UserCreate, UserUpdate  # Pydantic схема

from utils.hash_password import get_password_hash


async def create_user(session: AsyncSession, user: UserCreate):
    """Создание нового пользователя"""

    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user_by_id(session: AsyncSession, id: int) -> User | None:
    """Нахождение пользователя по его ID"""

    return await session.get(User, id)


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """Нахождение пользователя по его username"""

    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Нахождение пользователя по его email"""

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_users(session: AsyncSession) -> list[User]:
    """Получение всех пользователей"""

    stmt = select(User).order_by(User.id)
    result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def update_user(
    session: AsyncSession, user_update: UserUpdate, user_id: int
) -> User | None:
    """Обновление данных пользователя"""

    stmt = (
        update(User)
        .where(
            and_(
                User.email == user_update.email, User.username == user_update.username
            ),
        )
        .values(
            email=user_update.email if user_update.email else None,
            username=user_update.username if user_update.username else None,
            password=(
                get_password_hash(str(user_update.password))
                if user_update.password
                else None
            ),
        )
    )

    await session.execute(stmt)
    await session.commit()

    updated_user = await get_user_by_id(session, user_id)
    if not updated_user:
        return None

    return updated_user


async def delete_user(
    session: AsyncSession,
    user_id: int,
) -> bool:
    """Удаление пользователя"""

    user = await get_user_by_id(session, user_id)
    if not user:
        return False

    stmt = delete(User).where(User.id == user_id)
    await session.execute(stmt)
    await session.commit()

    return True
