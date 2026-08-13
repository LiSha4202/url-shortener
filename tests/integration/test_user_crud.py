import pytest
from crud.user_crud import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    get_all_users,
    update_user,
    delete_user,
)
from core.schemas.user_schema import UserCreate, UserUpdate
from models.users_model import User


@pytest.mark.asyncio
class TestUserCRUD:

    async def test_create_user(self, db_session):
        """Тест создания пользователя"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password",
        )

        new_user = await create_user(db_session, user_data)

        assert new_user.id is not None
        assert new_user.username == "testuser"
        assert new_user.email == "test@example.com"
        # Пароль должен быть зашифрован, а не равен исходному
        assert new_user.password != "password"

    async def test_get_user_by_id(self, db_session):
        """Тест получения пользователя по ID"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password",
        )
        created_user = await create_user(db_session, user_data)

        found_user = await get_user_by_id(db_session, created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id

    async def test_get_user_by_username(self, db_session):
        """Тест получения пользователя по username"""
        user_data = UserCreate(
            username="user",
            email="user@example.com",
            password="user_password",
        )
        created_user = await create_user(db_session, user_data)

        found_user = await get_user_by_username(db_session, created_user.username)

        assert found_user is not None
        assert found_user.username == "user"

    async def test_get_user_by_username_not_found(self, db_session):
        """Тест получения несуществующего пользователя по username"""
        user = await get_user_by_username(db_session, "nonexistened_user")
        assert user is None

    async def test_get_user_by_email(self, db_session):
        """Тест получения пользователя по email"""
        user_data = UserCreate(
            username="unique_user",
            email="unique@example.com",
            password="uniquepassword",
        )
        created_user = await create_user(db_session, user_data)

        found_user = await get_user_by_email(db_session, created_user.email)

        assert found_user is not None
        assert found_user.email == "unique@example.com"

    async def test_get_all_users(self, db_session):
        """Тест получения списка всех пользователей"""
        for i in range(3):
            await create_user(
                db_session,
                UserCreate(
                    username=f"user{i}",
                    email=f"user{i}@test.com",
                    password="password",
                ),
            )

        users = await get_all_users(db_session)
        assert len(users) == 3
        assert all(isinstance(u, User) for u in users)

    async def test_update_user(self, db_session):
        """Тест обновления данных пользователя"""
        user_data = UserCreate(
            username="oldname",
            email="old@test.com",
            password="oldpassword",
        )
        created_user = await create_user(db_session, user_data)

        update_data = UserUpdate(
            username="newname",
            email="new@test.com",
            password="newpassword",
        )

        updated_user = await update_user(db_session, update_data, created_user.id)

        assert updated_user is not None
        assert updated_user.username == "newname"
        assert updated_user.email == "new@test.com"
        assert updated_user.password != "newpass"  # Password should be hashed

    async def test_update_user_not_found(self, db_session):
        """Тест обновления несуществующего пользователя"""
        result = await update_user(db_session, UserUpdate(username="new"), 999)  # type: ignore
        assert result is None

    async def test_delete_user(self, db_session):
        """Тест удаления пользователя"""
        user_data = UserCreate(
            username="todelte",
            email="del@test.com",
            password="password",
        )
        created_user = await create_user(db_session, user_data)

        result = await delete_user(db_session, created_user.id)
        assert result is True

        deleted_user = await get_user_by_id(db_session, created_user.id)
        assert deleted_user is None

    async def test_delete_user_not_found(self, db_session):
        """Тест удаления несуществующего пользователя"""
        result = await delete_user(db_session, 999)
        assert result is False
