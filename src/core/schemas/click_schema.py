from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, IPvAnyAddress


class ClickLogResponse(BaseModel):
    """Схема для записи подробной информации о пользователе,
    нажавшим на ссылку."""

    id: int = Field(
        ...,
        description="ID записи о клике",
    )

    device_type: Optional[str] = Field(
        ...,
        description="Тип устройства пользователя",
    )

    browser: Optional[str] = Field(
        ...,
        description="Браузер, с помощью которого пользователь открыл сайт",
    )

    ip_address: Optional[IPvAnyAddress] = Field(
        ...,
        description="ip-адрес пользователя",
    )

    created_at: Optional[datetime] = Field(
        ...,
        description="Время создания записи",
    )

    class Config:
        from_attributes = True
