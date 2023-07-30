from src.Entities.base import Base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, RootModel
from typing import List


class Menu(Base):
    """Класс Menu описывает структуру таблицы menus: 3 столбца id, title и description, отнаследованных от базового
    класса"""
    __tablename__ = "menus"

    submenu = relationship('Submenu', back_populates='menu', cascade="all, delete-orphan")


class MenuModel(BaseModel):
    id: str
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class MenuCreateModel(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True


class MenuListModel(RootModel):
    root: List[MenuModel]
