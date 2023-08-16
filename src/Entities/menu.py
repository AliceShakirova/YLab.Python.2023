from functools import reduce

from pydantic import BaseModel, RootModel
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from src.Entities.base import Base


class Menu(Base):
    """Класс Menu описывает структуру таблицы menus: 3 столбца id, title и description, отнаследованных от базового
    класса"""
    __tablename__ = 'menus'

    submenus = relationship('Submenu', back_populates='menu', cascade='all, delete-orphan',
                            passive_deletes=True, lazy='joined')

    @hybrid_property
    def submenus_count(self):
        return len(self.submenus)

    @hybrid_property
    def dishes_count(self):
        return reduce(lambda self, submenu: submenu.dishes_count, self.submenus, 0)

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
