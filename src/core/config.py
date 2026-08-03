from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    """Конфигурация main.py файла"""

    host: str = "0.0.0.0"  # IP-адрес сервера
    port: int = 8000  # Порт
    reload: bool = True  # Автоматическая перезагрузка сервера при изменении кода


class LinkSchemaConfig(BaseModel):
    """Конфигурация значений для core/schemas/link_schema.py файла"""

    # SHORTCODE - Length Configuration
    shortcode_min_length: int = 4  # Минимальная длина короткой ссылки
    shortcode_max_length: int = 14  # Максимальная длина короткой ссылки

    # SHORTCODE - EXPIRE IN DAYS Configuration
    expire_in_days_min_length: int = (
        1  # Мин. количество дней, за которое ссылка будет действовать
    )
    expire_in_days_max_length: int = (
        365  # Макс. количество дней, за которое ссылка будет действовать
    )


class UserSchemaConfig(BaseModel):
    """Конфигурация значений для core/schemas/user_schema.py файла"""

    # Username - Length Configuration
    username_min_length: int = 3  # Минимальная длина никнейма
    username_max_length: int = 20  # Максимальная длина никнейма

    # Password - Length Configuration
    password_min_length: int = 8  # Минимальная длина пароля


class SetCookieConfig(BaseModel):
    key: str = "access_token"
    httponly: bool = True  # Запрет доступа через JS
    samesite: str = "lax"  # Защита от CSRF
    secure: bool = False  # True для HTTPS
    max_age: int = 3600  # 1 час


class DataBaseSettings(BaseModel):
    """Настройки базы данных"""

    url: PostgresDsn  # (DSN - Data Source Name) - Информация для подключения к базе данных, т.е. ссылка на базу данных
    echo: bool = False  # Логирование SQL-запросов (от слова Лог - запись)
    pool_pre_ping: bool = True  # Проверка "жизни" соединения
    pool_size: int = (
        5  # Размер пула соединений (активных) Пул - предварительно подготовленный набор соединений к БД
    )
    max_overflow: int = 10  # Максимальное превышение соединений сверх pool_size
    autocommit: bool = False  # Автоматический коммит (т.е. авто-сохранение)
    autoflush: bool = False  # Авто-флеш (только при commit)
    expire_on_commit: bool = False  # Аннулирование значений после сохранения в БД

    """Используется для автоматического подписания ключей в миграциях alembic"""
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",  # index
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",  # Unique Constraint
        "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check Constraint
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # ForeignKey
        "pk": "pk_%(table_name)s",  # Primary Key
    }


class JWTSettings(BaseModel):
    """Настройки JWT-аутентификации"""

    # JWT - Secret key
    jwt_secret_key: str

    # JWT - Алгоритм шифрования
    algorithm: str = "HS256"

    # JWT - Срок действия вида токенов
    access_token_expire_minutes: int = 30  # Access-Token при входе в систему (МИНУТ)
    refresh_token_expire_days: int = 7  # Refresh-token для обновления Access-T (ДНИ.)


class RedisConfig(BaseModel):
    """Настройки Redis"""

    # REDIS - URL
    redis_url: str = "redis://redis:6379/0"


class Settings(BaseSettings):
    """Основной класс, принимающий все классы из файла config.py для использования в других файлах"""

    model_config = SettingsConfigDict(  # Настройки для добычи данных из .env
        env_file=(".env"),  # Файл с переменными окружения
        case_sensitive=False,  # Чувствительность к регистру
        env_nested_delimiter="__",  # Разделение
        env_prefix="APP_CONFIG__",  # Префикс, т.е. начало всех переменных
    )

    run: RunConfig = RunConfig()
    db: DataBaseSettings
    ls: LinkSchemaConfig = LinkSchemaConfig()
    us: UserSchemaConfig = UserSchemaConfig()
    jwt: JWTSettings
    sc: SetCookieConfig = SetCookieConfig()
    rds: RedisConfig = RedisConfig()


settings = Settings()  # type: ignore
