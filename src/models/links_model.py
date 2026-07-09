import datetime

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from .users_model import User


class Link(Base):
    """Шаблон для SQL, Link хранит данные об укороченной ссылке пользователя"""

    __tablename__ = "link"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(unique=True, index=True)
    original_url: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    expires_at: Mapped[datetime.datetime] = mapped_column()
    created_on: Mapped[datetime.datetime] = mapped_column()
    clicks_count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User | None"] = relationship(  # Связь Many-to-One
        back_populates="link",
        lazy="select",
    )
