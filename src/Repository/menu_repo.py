from typing import Any

from sqlalchemy import Row, func, select

from src.Db.database import get_session
from src.Entities.dish import Dish
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu


class MenuRepo:
    async def create_menu(self, title: str, description: str) -> Menu:
        async with get_session() as db:
            new_menu = Menu(title=title, description=description)
            db.add(new_menu)
            await db.commit()
            await db.refresh(new_menu)
            return new_menu

    async def get_all_menus(self) -> list[type[Menu]]:
        async with get_session() as db:
            all_menus = (await db.scalars(select(Menu))).all()
            return all_menus

    async def get_menu(self, menu_id: str) -> Menu | None:
        async with get_session() as db:
            return (await db.scalars(select(Menu).where(Menu.id == menu_id))).first()

    async def update_menu(self, menu_id: str, title: str, description: str) -> Menu | None:
        async with get_session() as db:
            menu_to_update = (await db.scalars(select(Menu).where(Menu.id == menu_id))).first()
            if menu_to_update:
                menu_to_update.title = title
                menu_to_update.description = description
                await db.commit()
                await db.refresh(menu_to_update)
            return menu_to_update

    async def delete_menu(self, menu_id: str) -> bool:
        async with get_session() as db:
            menu_to_delete = (await db.scalars(select(Menu).where(Menu.id == menu_id))).first()
            if not menu_to_delete:
                return False
            await db.delete(menu_to_delete)
            await db.commit()
            return True

    async def get_submenus_and_dishes_counts(self, menu_id: str) -> Row[tuple[Any, ...] | Any]:
        async with get_session() as db:
            result = (await db.execute(
                select(func.count(func.distinct(Submenu.id)),
                       func.count(func.distinct(Dish.id)))
                .select_from(Submenu)
                .join(Dish, Dish.submenu_id == Submenu.id, isouter=True)
                .where(Submenu.menu_id == menu_id))).one()
            return result

    async def get_all_menus_submenus_and_dishes(self):
        async with get_session() as db:
            return (await db.scalars(
                select(Menu, Submenu, Dish)
                .join(Submenu, Submenu.menu_id == Menu.id, isouter=True)
                .where(Submenu.menu_id == Menu.id)
                .join(Dish, Submenu.id == Dish.submenu_id, isouter=True)
                .where(Submenu.menu_id == Menu.id)
                .order_by(Menu.id)
            )).all()
