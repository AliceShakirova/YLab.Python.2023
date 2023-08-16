from pydantic import BaseModel, RootModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column, relationship

from src.Entities.base import Base


class Submenu(Base):
    """Класс Submenu описывает структуру таблицы submenus: 3 столбца id, title и descriptionб относледованных от
    базового класса, + дополнительный столбец menu_id, связывющий таблицу submenu с таблицей menus"""
    __tablename__ = 'submenus'

    menu_id = mapped_column(String, ForeignKey('menus.id', ondelete='CASCADE'), nullable=False)
    menu = relationship('Menu', back_populates='submenus', single_parent=True, innerjoin=True)
    dishes = relationship('Dish', back_populates='submenu', cascade='all, delete-orphan',
                          passive_deletes=True, lazy='joined')

    @hybrid_property
    def dishes_count(self):
        return len(self.dishes)

    def __init__(self, title: str, description: str, menu_id: str, id: str | None = None) -> None:
        super().__init__(title, description, id)
        self.menu_id = menu_id


class SubmenuModel(BaseModel):
    id: str
    title: str
    description: str
    dishes_count: int


class SubmenuCreateModel(BaseModel):
    title: str
    description: str

    model_config = {'from_attributes': True, 'validate_assignment': True}


class SubmenuListModel(RootModel):
    root: list[SubmenuModel]
