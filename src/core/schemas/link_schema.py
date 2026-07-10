from datetime import datetime
from typing import Optional, Dict

from pydantic import Field, BaseModel, HttpUrl
from pydantic.types import constr

# Алиас для валидации кастомной ссылки
ShortCode = constr(
    strip_whitespace=True, min_length=4, max_length=14, pattern=r"^[a-zA-Z0-9_-]+$"
)


class LinkBase(BaseModel):
    """Базовая модель, не используется сама по себе"""

    original_url: HttpUrl = Field(
        ...,
        description="Оригинальный URL (Должен начинаться с http:// или https://)",
    )


class LinkCreate(LinkBase):
    """Модель для создания ссылки"""

    custom_code: Optional[ShortCode] = Field(  # type: ignore
        None,
        description=(
            "Уникальный сокращённый код URL для оригинального URL"
            "Имеется возможность создавать свой код; если он не указан, будет создан случайный код"
        ),
    )

    expires_in_days: Optional[int] = Field(
        ge=1,  # только положительные числа
        le=365,  # максимум 1 год
        description=("Время истечения ссылки (Опционально)" "По умолчанию не истекает"),
    )


class LinkResponse(BaseModel):
    """Модель для ответа серверу, когда ссылка уже создана"""

    short_code: str = Field(
        ...,
        description="Сгенерированный или кастомный код ссылки",
    )

    short_url: str = Field(
        ...,
        description="Полный URL с укороченной ссылкой",
    )

    original_url: str = Field(
        ...,
        description="Оригинальный URL",
    )

    clicks_count: int = Field(
        ...,
        description="Количество кликов по короткому URL",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Время создания короткой ссылки",
    )

    expired_at: Optional[datetime] = Field(
        None,
        description="(необязательно) Время истечения срока действия",
    )


class LinkStats(BaseModel):
    """Статистика по короткой ссылке"""

    short_code: str = Field(
        ...,
        description="Уникальный короткий код для ссылки",
    )

    total_clicks_count: int = Field(
        ...,
        description="Общее количество кликов по ссылке",
    )

    first_click: Optional[datetime] = Field(
        ...,
        description="Время 1 клика по ссылке",
    )

    last_click: Optional[datetime] = Field(
        ...,
        description="Последний клик по ссылке",
    )

    clicks_by_day: Dict[str, int] = Field(
        default_factory=dict,
        description="Количество переходов за день",
    )
