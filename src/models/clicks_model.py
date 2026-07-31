from datetime import datetime

from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from models.links_model import Link


class ClickLog(Base):

    __tablename__ = "click_log"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("link.id"), nullable=False)

    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow(), index=True)

    link: Mapped["Link"] = relationship(back_populates="click_log")

    def __str__(self):
        return f"ClickLog(id={self.id}, link_id={self.link_id})"
