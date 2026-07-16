from datetime import datetime

from typing import TYPE_CHECKING

from pydantic import HttpUrl

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from .users_model import User


class Link(Base):
    """Шаблон для SQL, Link хранит данные об укороченной ссылке пользователя"""

    __tablename__ = "link"  # type: ignore

    # Базовые поля
    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(unique=True, index=True)
    original_url: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    expires_at: Mapped[datetime] = mapped_column()
    created_on: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    # Поля для статистики (Опционально)
    first_click: Mapped[datetime] = mapped_column(nullable=True)
    last_click: Mapped[datetime] = mapped_column(nullable=True)
    clicks_count: Mapped[int] = mapped_column(default=0)

    # JSON-поле для хранения агрегации по дням
    clicks_by_day: Mapped[dict[str, int]] = mapped_column(
        JSON,
        nullable=True,
        default={},
    )

    user: Mapped["User | None"] = relationship(  # Связь Many-to-One
        back_populates="links",
        lazy="select",
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, short_code={self.short_code!r})"
        )

    def __repr__(self):
        return str(self)
