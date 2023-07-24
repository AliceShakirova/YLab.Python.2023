from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from Entities.base import Base


class Submenu(Base):
    """Класс Submenu описывает структуру таблицы submenus: 3 столбца id, title и descriptionб относледованных от
    базового класса, + дополнительный столбец menu_id, связывющий таблицу submenu с таблицей menus"""
    __tablename__ = "submenus"

    menu_id = mapped_column(String, ForeignKey("menus.id"), nullable=False)
    menu = relationship('Menu', back_populates='submenu', single_parent=True)
    dish = relationship('Dish', back_populates='submenu', cascade="all, delete-orphan")

    def __init__(self, title, description, menu_id):
        Base.__init__(self, title, description)
        self.menu_id = menu_id
