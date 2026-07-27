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

    current_user = await get_user_by_id(session, user_id)
    if not current_user:
        return None

    values = {}
    if user_update.username is not None:
        values["username"] = user_update.username
    if user_update.email is not None:
        values["email"] = user_update.email
    if user_update.password is not None:
        values["password"] = get_password_hash(user_update.password)

    if not values:
        return current_user

    stmt = update(User).where(User.id == user_id).values(**values)
    await session.execute(stmt)
    await session.commit()

    return await get_user_by_id(session, user_id)


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
