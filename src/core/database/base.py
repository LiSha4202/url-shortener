from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

from src.core.config import settings

from src.utils.case_converter import camel_case_to_snake_case


class Base(DeclarativeBase):
    """База для SQLAlchemy для управления другими шаблонами таблиц"""

    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"
