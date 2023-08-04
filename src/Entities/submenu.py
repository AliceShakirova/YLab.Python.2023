from pydantic import BaseModel, RootModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship

from src.Entities.base import Base


class Submenu(Base):
    """Класс Submenu описывает структуру таблицы submenus: 3 столбца id, title и descriptionб относледованных от
    базового класса, + дополнительный столбец menu_id, связывющий таблицу submenu с таблицей menus"""
    __tablename__ = 'submenus'

    menu_id = mapped_column(String, ForeignKey('menus.id'), nullable=False)
    menu = relationship('Menu', back_populates='submenu', single_parent=True)
    dish = relationship('Dish', back_populates='submenu', cascade='all, delete-orphan')

    def __init__(self, title, description, menu_id):
        Base.__init__(self, title, description)
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
