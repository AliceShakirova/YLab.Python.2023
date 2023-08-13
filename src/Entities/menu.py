from pydantic import BaseModel, RootModel
from sqlalchemy.orm import relationship

from src.Entities.base import Base


class Menu(Base):
    """Класс Menu описывает структуру таблицы menus: 3 столбца id, title и description, отнаследованных от базового
    класса"""
    __tablename__ = 'menus'

    submenu = relationship('Submenu', back_populates='menu', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, title: str, description: str, id: str | None = None):
        super().__init__(title, description, id)


class MenuModel(BaseModel):
    id: str
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class MenuCreateModel(BaseModel):
    title: str
    description: str

    model_config = {'from_attributes': True, 'validate_assignment': True}


class MenuListModel(RootModel):
    root: list[MenuModel]
