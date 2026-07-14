from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    async_scoped_session,
)

from asyncio import current_task

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
        expire_on_commit: bool,
    ) -> None:
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            max_overflow=max_overflow,
            pool_size=pool_size,
            pool_pre_ping=pool_pre_ping,
        )

        self.session_factory = async_sessionmaker(
            autocommit=autocommit,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            bind=self.engine,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncSession:  # type: ignore
        async with self.session_factory() as session:
            yield session  # type: ignore
            await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:  # type: ignore
        session = self.get_scoped_session()
        yield session  # type: ignore
        await session.close()


db_engine = DataBaseEngine(
    url=str(settings.db.url),
    echo=settings.db.echo,
    pool_pre_ping=settings.db.pool_pre_ping,
    autocommit=settings.db.autocommit,
    autoflush=settings.db.autoflush,
    max_overflow=settings.db.max_overflow,
    pool_size=settings.db.pool_size,
    expire_on_commit=settings.db.expire_on_commit,
)
