from pydantic import BaseModel


class UserModel(BaseModel):
    user: str
    email: str
    password_hashed: str
    created_at: int


class UserCreate(UserModel):
    pass


class UserUpdate(UserModel):
    pass
