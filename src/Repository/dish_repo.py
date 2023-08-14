from _decimal import Decimal
from sqlalchemy import delete, func, select

from src.Db.database import get_session
from src.Entities.dish import Dish


class DishRepo:
    @staticmethod
    async def create_dish(title: str, description: str, price: Decimal, submenu_id: str) -> Dish:
        async with get_session() as db:
            new_dish = Dish(title=title, description=description, price=price, submenu_id=submenu_id)
            db.add(new_dish)
            await db.commit()
            await db.refresh(new_dish)
            return new_dish

    @staticmethod
    async def create_dish_from_object(dish: Dish) -> Dish:
        async with get_session() as db:
            db.add(dish)
            await db.commit()
            await db.refresh(dish)
            return dish

    @staticmethod
    async def get_dishes_of_submenu(submenu_id: str) -> list[type[Dish]]:
        async with get_session() as db:
            dishes_of_submenu = (await db.scalars(select(Dish).where(Dish.submenu_id == submenu_id))).all()
            return dishes_of_submenu

    @staticmethod
    async def get_dishes_count(submenu_id: str) -> int:
        async with get_session() as db:
            return (await db.scalars(select(func.count(Dish.id)).where(Dish.submenu_id == submenu_id))).one()

    @staticmethod
    async def get_dish(dish_id: str, submenu_id: str) -> Dish | None:
        async with get_session() as db:
            dish = await db.scalars(select(Dish).where(Dish.id == dish_id, Dish.submenu_id == submenu_id))
            return dish.first()

    @staticmethod
    async def update_dish(dish_id: str, title: str, description: str, price: str,
                          submenu_id: str) -> Dish | None:
        async with get_session() as db:
            dish_to_update = (await db.scalars(select(Dish).where(Dish.id == dish_id,
                                                                  Dish.submenu_id == submenu_id))).first()
            if dish_to_update is not None:
                dish_to_update.title = title
                dish_to_update.description = description
                dish_to_update.price = price
                await db.commit()
                await db.refresh(dish_to_update)
            return dish_to_update

    @staticmethod
    async def update_dish_from_object(dish: Dish) -> Dish | None:
        async with get_session() as db:
            dish_to_update = (await db.scalars(select(Dish).where(Dish.id == dish.id,
                                                                  Dish.submenu_id == dish.submenu_id))).first()
            if dish_to_update is not None:
                dish_to_update.title = dish.title
                dish_to_update.description = dish.description
                dish_to_update.price = dish.price
                await db.commit()
                await db.refresh(dish_to_update)
            return dish_to_update

    @staticmethod
    async def delete_dish(dish_id: str, submenu_id: str) -> bool:
        async with get_session() as db:
            dish_to_delete = (await db.scalars(select(Dish).filter_by(id=str(dish_id), submenu_id=submenu_id))).first()
            if not dish_to_delete:
                return False
            await db.delete(dish_to_delete)
            await db.commit()
            return True

    @staticmethod
    async def get_dishes_of_submenus(ids: list) -> list[type[Dish]]:
        async with get_session() as db:
            return (await db.scalars(select(Dish).filter(Dish.submenu_id.in_(ids)))).all()

    @staticmethod
    async def delete_dishes(dishes: set):
        async with get_session() as db:
            await db.execute(delete(Dish).where(Dish.id.in_(dishes)))
