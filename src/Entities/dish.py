from decimal import Decimal
from typing import SupportsRound

from pydantic import BaseModel, RootModel, condecimal, field_validator
from pydantic.v1 import ConfigDict
from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship

from src.Entities.base import Base


class Dish(Base):
    """Класс Dish описывает структуру таблицы dishes: 3 столбца id, title и descriptionб относледованных от
    базового класса, + дополнительные столбец submenu_id, связывющий таблицу dishes с таблицей submenu, и столбец
    price"""
    __tablename__ = 'dishes'

    submenu_id = mapped_column(String, ForeignKey('submenus.id', ondelete='CASCADE'), nullable=False)
    price = mapped_column(DECIMAL(10, 2))
    submenu = relationship('Submenu', back_populates='dishes', single_parent=True, innerjoin=True)

    def __init__(self, title: str, description: str, submenu_id: str, price: Decimal, id: str | None = None) -> None:
        super().__init__(title, description, id)
        self.submenu_id = submenu_id
        self.price = price


class DishModel(BaseModel):
    id: str
    title: str
    description: str
    price: str

    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    @field_validator('price', mode='before')
    @classmethod
    def price_validator(cls, value: SupportsRound[Decimal]) -> str:
        # в случае десериализации из кэша будет строка
        if type(value) is str:
            return value
        return str(round(value, ndigits=2))


class DishCreateModel(BaseModel):
    title: str
    description: str
    price: condecimal(ge=0)  # type: ignore

    model_config = {'from_attributes': True, 'validate_assignment': True}


class DishListModel(RootModel):
    root: list[DishModel]
