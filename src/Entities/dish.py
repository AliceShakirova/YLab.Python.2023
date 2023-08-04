from decimal import Decimal

from pydantic import BaseModel, RootModel, condecimal, field_validator
from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship

from src.Entities.base import Base


class Dish(Base):
    """Класс Dish описывает структуру таблицы dishes: 3 столбца id, title и descriptionб относледованных от
    базового класса, + дополнительные столбец submenu_id, связывющий таблицу dishes с таблицей submenu, и столбец
    price"""
    __tablename__ = 'dishes'

    submenu_id = mapped_column(String, ForeignKey('submenus.id'), nullable=False)
    price = mapped_column(DECIMAL(5, 2))
    submenu = relationship('Submenu', back_populates='dish', single_parent=True)

    def __init__(self, title: str, description: str, submenu_id: str, price: Decimal):
        Base.__init__(self, title, description)
        self.submenu_id = submenu_id
        self.price = price


class DishModel(BaseModel):
    id: str
    title: str
    description: str
    price: str

    model_config = {'from_attributes': True, 'validate_assignment': True}

    @field_validator('price', mode='before')
    @classmethod
    def price_validator(cls, value: Decimal) -> str:
        return str(round(value, ndigits=2))


class DishCreateModel(BaseModel):
    title: str
    description: str
    price: condecimal(ge=0)  # type: ignore

    model_config = {'from_attributes': True, 'validate_assignment': True}


class DishListModel(RootModel):
    root: list[DishModel]
