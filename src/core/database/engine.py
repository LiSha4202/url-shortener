from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.config import settings


class DataBaseEngine:
    def __init__(
        self,
        url: str,
        echo: bool,
        pool_pre_ping: bool,
        autocommit: bool,
        autoflush: bool,
        max_overflow: int,
        pool_size: int,
    ) -> None:
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            max_overflow=max_overflow,
            pool_size=pool_size,
            pool_pre_ping=pool_pre_ping,
        )

        self.sessionmaker = async_sessionmaker(
            autocommit=autocommit,
            autoflush=autoflush,
            bind=self.engine,
        )


db_helper = DataBaseEngine(
    url=settings.db.url,
    echo=settings.db.echo,
    pool_pre_ping=settings.db.pool_pre_ping,
    autocommit=settings.db.autocommit,
    autoflush=settings.db.autoflush,
    max_overflow=settings.db.max_overflow,
    pool_size=settings.db.pool_size,
)
