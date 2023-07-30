from sqlalchemy import String, ForeignKey, DECIMAL
from sqlalchemy.orm import mapped_column, relationship
from src.Entities.base import Base
from pydantic import BaseModel, condecimal, field_validator, RootModel
from typing import List
from decimal import Decimal


class Dish(Base):
    """Класс Dish описывает структуру таблицы dishes: 3 столбца id, title и descriptionб относледованных от
    базового класса, + дополнительные столбец submenu_id, связывющий таблицу dishes с таблицей submenu, и столбец
    price"""
    __tablename__ = 'dishes'

    submenu_id = mapped_column(String, ForeignKey("submenus.id"), nullable=False)
    price = mapped_column(DECIMAL(5, 2))
    submenu = relationship('Submenu', back_populates='dish', single_parent=True)

    def __init__(self, title, description, submenu_id, price=0):
        Base.__init__(self, title, description)
        self.submenu_id = submenu_id
        self.price = price


class DishModel(BaseModel):
    id: str
    title: str
    description: str
    price: str

    @field_validator('price', mode= 'before')
    @classmethod
    def price_validator(cls, value: Decimal) -> str:
        return str(round(value, ndigits=2))

    class Config:
        orm_mode = True
        validate_assignment = True


class DishCreateModel(BaseModel):
    title: str
    description: str
    price: condecimal(ge=0)

    class Config:
        orm_mode = True


class DishListModel(RootModel):
    root: List[DishModel]
