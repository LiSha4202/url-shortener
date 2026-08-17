from datetime import datetime, timezone

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from .links_model import Link


class User(Base):
    """Шаблон для SQL, User хранит данные о пользователе"""

    __tablename__ = "user"  # type: ignore
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    links: Mapped[list["Link"]] = relationship(  # Связь Many-to-One
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self):
        return str(self)
