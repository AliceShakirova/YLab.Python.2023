from Entities.base import Base
from sqlalchemy.orm import relationship


class Menu(Base):
    """Класс Menu описывает структуру таблицы menus: 3 столбца id, title и description, отнаследованных от базового
    класса"""
    __tablename__ = "menus"

    submenu = relationship('Submenu', back_populates='menu', cascade="all, delete-orphan")
