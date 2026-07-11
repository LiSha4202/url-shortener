from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped, relationship

from core.database.base import Base
from .links_model import Link


class User(Base):
    """Шаблон для SQL, User хранит данные о пользователе"""

    __tablename__ = "user"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    created_at: Mapped[float] = mapped_column(default=datetime)

    links: Mapped[list["Link"]] = relationship(  # Связь Many-to-One
        back_populates="user",
        cascade="all, delete-orphan",
    )
