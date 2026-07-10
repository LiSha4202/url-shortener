from datetime import datetime

from typing import TYPE_CHECKING, Optional, Dict, Any

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
    created_on: Mapped[datetime] = mapped_column()
    clicks_count: Mapped[int] = mapped_column(default=0)

    # Поля для статистики (Опционально)
    first_click: Mapped[datetime] = mapped_column(nullable=True)
    last_click: Mapped[datetime] = mapped_column(nullable=True)

    # JSON-поле для хранения агрегации по дням
    clicks_by_day: Mapped[dict[str, int]] = mapped_column(
        JSON,
        nullable=True,
        default={},
    )

    user: Mapped["User | None"] = relationship(  # Связь Many-to-One
        back_populates="link",
        lazy="select",
    )
