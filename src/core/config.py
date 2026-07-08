from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    """Конфигурация main файла"""

    host: str = "0.0.0.0"
    port: int = 8000


class DataBaseSettings(BaseSettings):
    """Настройки базы данных"""

    url: PostgresDsn  # (DSN - Data Source Name) - Информация для подключения к базе данных, т.е. ссылка на базу данных (далее в Settings будут его настройки )
    echo: bool = False  # Логирование SQL-запросов (от слова Лог - запись)
    pool_pre_ping: bool = True  # Проверка "жизни" соединения
    pool_size: int = 5  # Размер пула соединений (активных)
    max_overflow: int = 10  # Максимальное превышение соединений сверх pool_size
    autocommit: bool = False  # Автоматический коммит (т.е. авто-сохранение)
    autoflush: bool = False  # Авто-флеш (только при commit)

    """Используется для автоматического подписания ключей в миграциях alembic"""
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",  # index
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",  # Unique Constraint
        "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check Constraint
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # ForeignKey
        "pk": "pk_%(table_name)s",  # Primary Key
    }


class Settings(BaseSettings):
    """Основной класс, принимающий все классы из этого файла для использования в других файлах"""

    model_config = SettingsConfigDict(  # Настройки DSN
        env_file=".env",  # Файл с переменными окружения
        case_sensitive=False,  # Чувствительность к регистру
        env_nested_delimiter="__",  # Разделение
        env_prefix="APP_CONFIG__",  # Префикс, т.е. начало всех переменных
    )

    run: RunConfig = RunConfig()
    db: DataBaseSettings


settings = Settings()  # type: ignore
