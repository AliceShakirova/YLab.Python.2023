from sqlalchemy import Row, delete, func, select
from sqlalchemy.orm import joinedload

from src.Db.database import get_session
from src.Entities.dish import Dish
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu


class MenuRepo:
    @staticmethod
    async def create_menu(title: str, description: str) -> Menu:
        async with get_session() as db:
            new_menu = Menu(title=title, description=description)
            db.add(new_menu)
            await db.commit()
            await db.refresh(new_menu)
            return new_menu

    @staticmethod
    async def create_menu_from_object(menu: Menu) -> Menu:
        async with get_session() as db:
            db.add(menu)
            await db.commit()
            await db.refresh(menu)
            return menu

    @staticmethod
    async def get_all_menus() -> list[type[Menu]]:
        async with get_session() as db:
            all_menus = (await db.scalars(select(Menu))).unique().all()
            return all_menus

    @staticmethod
    async def get_menu(menu_id: str) -> Menu | None:
        async with get_session() as db:
            return (await db.scalars(select(Menu).where(Menu.id == menu_id))).first()

    @staticmethod
    async def update_menu(menu_id: str, title: str, description: str) -> Menu | None:
        async with get_session() as db:
            menu_to_update = (await db.scalars(select(Menu).where(Menu.id == menu_id))).first()
            if menu_to_update:
                menu_to_update.title = title
                menu_to_update.description = description
                await db.commit()
                await db.refresh(menu_to_update)
            return menu_to_update

    @staticmethod
    async def update_menu_from_object(menu: Menu) -> Menu | None:
        async with get_session() as db:
            menu_to_update = (await db.scalars(select(Menu).where(Menu.id == menu.id))).first()
            if menu_to_update:
                menu_to_update.title = menu.title
                menu_to_update.description = menu.description
                await db.commit()
                await db.refresh(menu_to_update)
            return menu_to_update

    @staticmethod
    async def delete_menu(menu_id: str) -> bool:
        async with get_session() as db:
            menu_to_delete = (await db.scalars(select(Menu).where(Menu.id == menu_id))).first()
            if not menu_to_delete:
                return False
            await db.delete(menu_to_delete)
            await db.commit()
            return True

    @staticmethod
    async def get_submenus_and_dishes_counts(menu_id: str) -> Row[tuple[int, int]]:
        async with get_session() as db:
            result = (await db.execute(
                select(func.count(func.distinct(Submenu.id)),
                       func.count(func.distinct(Dish.id)))
                .select_from(Submenu)
                .join(Dish, Dish.submenu_id == Submenu.id, isouter=True)
                .where(Submenu.menu_id == menu_id))).one()
            return result

    @staticmethod
    async def get_all_menus_submenus_and_dishes() -> list:
        async with get_session() as db:
            return (await db.scalars(
                select(Menu, Submenu, Dish)
                .join(Submenu, Submenu.menu_id == Menu.id, isouter=True)
                .where(Submenu.menu_id == Menu.id)
                .join(Dish, Submenu.id == Dish.submenu_id, isouter=True)
                .where(Submenu.menu_id == Menu.id)
                .order_by(Menu.id)
            )).all()

    @staticmethod
    async def get_full_tree() -> list[Menu]:
        async with get_session() as db:
            return (await db.scalars(
                select(Menu).options(joinedload(Menu.submenus).options(joinedload(Submenu.dishes)))
                .order_by(Menu.id)
            )).unique().all()

    @staticmethod
    async def delete_menus(menus: set) -> None:
        async with get_session() as db:
            await db.execute(delete(Menu).where(Menu.id.in_(menus)))
