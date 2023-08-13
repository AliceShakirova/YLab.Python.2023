import uuid

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    """Базовый класс, описывающий основную структуру будущих таблиц: 3 столбца id, title и description"""
    id = mapped_column(String, primary_key=True, unique=True, nullable=False)
    title = mapped_column(String, nullable=False)
    description = mapped_column(String)

    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
