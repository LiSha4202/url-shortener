from datetime import datetime
from typing import Optional, Dict

from pydantic import Field, BaseModel, HttpUrl, computed_field
from pydantic.types import constr

from core.config import settings

# Алиас для валидации кастомной ссылки
ShortCode = constr(
    strip_whitespace=True,
    min_length=settings.ls.shortcode_min_length,
    max_length=settings.ls.shortcode_max_length,
    pattern=r"^[a-zA-Z0-9_-]+$",
)


class LinkBase(BaseModel):
    """Базовая модель, не используется сама по себе"""

    original_url: HttpUrl = Field(
        ...,
        description="Оригинальный URL (Должен начинаться с http:// или https://)",
    )


class LinkCreate(LinkBase):
    """Модель для создания ссылки"""

    short_code: Optional[ShortCode] = Field(  # type: ignore
        None,
        description=(
            "Уникальный сокращённый код URL для оригинального URL"
            "Имеется возможность создавать свой код; если он не указан, будет создан случайный код"
        ),
    )

    expires_at: Optional[int] = Field(  # Измеряется в днях
        default=None,
        ge=settings.ls.expire_in_days_min_length,  # Минимальный срок жизни ссылки
        le=settings.ls.expire_in_days_max_length,  # Максимальный срок жизни ссылки
        description=("Время истечения ссылки (Опционально)" "По умолчанию не истекает"),
    )


class LinkResponse(BaseModel):
    """Модель для ответа серверу, когда ссылка уже создана"""

    short_code: str = Field(
        ...,
        description="Сгенерированный или кастомный код ссылки",
    )

    original_url: str = Field(
        ...,
        description="Оригинальный URL",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Время создания короткой ссылки",
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="(необязательно) Время истечения срока действия",
    )

    @computed_field
    @property
    def short_url(self) -> str:
        """Полный URL с короткой ссылкой"""
        return f"http://{settings.run.host}:{settings.run.port}/{self.short_code}"


class LinkStats(BaseModel):
    """Статистика по короткой ссылке"""

    short_code: str = Field(
        ...,
        description="Уникальный короткий код для ссылки",
    )

    clicks_count: int = Field(
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


class LinkStatsAll(BaseModel):
    """Общая статистика по всем ссылкам"""

    total_clicks: int = Field(
        ...,
        description="Общее количество кликов по всем ссылкам",
    )

    total_links: int = Field(
        ...,
        description="Общее количество ссылок",
    )

    active_links: int = Field(
        ...,
        description="Количество активных (не удаленных)ссылок",
    )

    expired_links: int = Field(
        ...,
        description="Количество просроченых (удаленных) ссылок",
    )

    class Config:
        from_attributes = True


class LinkStatsTop(BaseModel):
    """Топ популярных ссылок"""

    short_code: str = Field(
        ...,
        description="Короткий код ссылки",
    )

    original_url: str = Field(
        ...,
        description="Оригинальная ссылка",
    )

    @computed_field
    @property
    def short_url(self) -> str:
        """Полный URL с короткой ссылкой"""
        return f"http://{settings.run.host}:{settings.run.port}/{self.short_code}"

    click_count: int = Field(
        ...,
        description="Количество кликов по ссылке",
    )

    created_at: datetime = Field(
        ...,
        description="Дата создания ссылки",
    )

    class Config:
        from_attributes = True


class LinksMe(BaseModel):
    """Схема данных о ссылке, только по user_id"""

    user_id: int = Field(
        ...,
        description="ID пользователя",
    )

    short_code: str = Field(
        ...,
        description="Сгенерированный или кастомный код ссылки",
    )

    @computed_field
    @property
    def short_url(self) -> str:
        """Полный URL с короткой ссылкой"""
        return f"http://{settings.run.host}:{settings.run.port}/{self.short_code}"

    original_url: str = Field(
        ...,
        description="Оригинальный URL",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Время создания короткой ссылки",
    )

    expires_at: Optional[datetime] = Field(
        None,
        description="(необязательно) Время истечения срока действия",
    )

    class Config:
        from_attributes = True


class LinkUpdate(BaseModel):
    """Схема для обновления ссылки"""

    original_url: str = Field(
        ...,
        description="Новый оригинальный URL",
    )

    expires_at: Optional[int] = Field(
        default=None,
        ge=settings.ls.expire_in_days_min_length,  # Минимальный срок жизни ссылки
        le=settings.ls.expire_in_days_max_length,  # Максимальный срок жизни ссылки
        description=("Время истечения ссылки (Опционально)" "По умолчанию не истекает"),
    )
