from sqlalchemy import String, ForeignKey, DECIMAL
from sqlalchemy.orm import mapped_column, relationship
from Entities.base import Base


class Dish(Base):
    """Класс Dish описывает структуру таблицы dishes: 3 столбца id, title и descriptionб относледованных от
    базового класса, + дополнительные столбец submenu_id, связывющий таблицу dishes с таблицей submenu, и столбец
    price"""
    __tablename__ = 'dishes'

    submenu_id = mapped_column(String, ForeignKey("submenus.id"), nullable=False)
    price = mapped_column(DECIMAL)
    submenu = relationship('Submenu', back_populates='dish', single_parent=True)

    def __init__(self, title, description, submenu_id, price=0):
        Base.__init__(self, title, description)
        self.submenu_id = submenu_id
        self.price = price
