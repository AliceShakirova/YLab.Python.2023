from sqlalchemy import delete, func, select

from src.Db.database import get_session
from src.Entities.submenu import Submenu


class SubmenuRepo:
    @staticmethod
    async def create_submenu(title: str, description: str, menu_id: str) -> Submenu:
        async with get_session() as db:
            new_submenu = Submenu(title=title, description=description, menu_id=menu_id)
            db.add(new_submenu)
            await db.commit()
            await db.refresh(new_submenu)
            return new_submenu

    @staticmethod
    async def create_submenu_from_object(submenu: Submenu) -> Submenu:
        async with get_session() as db:
            db.add(submenu)
            await db.commit()
            await db.refresh(submenu)
            return submenu

    @staticmethod
    async def get_all_submenus(self) -> list[type[Submenu]]:
        async with get_session() as db:
            all_submenus = (await db.scalars(select(Submenu))).all()
            return all_submenus

    @staticmethod
    async def get_submenu(menu_id: str, submenu_id: str) -> Submenu | None:
        async with get_session() as db:
            return (await db.scalars(select(Submenu)
                                     .where(Submenu.id == submenu_id, Submenu.menu_id == menu_id))).first()

    @staticmethod
    async def update_submenu(submenu_id: str, title: str, description: str, menu_id: str) -> Submenu | None:
        async with get_session() as db:
            submenu_to_update = (await db.scalars(select(Submenu).where(Submenu.id == submenu_id,
                                                                        Submenu.menu_id == menu_id))).first()
            if submenu_to_update:
                submenu_to_update.title = title
                submenu_to_update.description = description
                await db.commit()
                await db.refresh(submenu_to_update)
            return submenu_to_update

    @staticmethod
    async def update_submenu_from_object(submenu: Submenu) -> Submenu | None:
        async with get_session() as db:
            submenu_to_update = (await db.scalars(select(Submenu).where(Submenu.id == submenu.id,
                                                                        Submenu.menu_id == submenu.menu_id))).first()
            if submenu_to_update:
                submenu_to_update.title = submenu.title
                submenu_to_update.description = submenu.description
                await db.commit()
                await db.refresh(submenu_to_update)
            return submenu_to_update

    @staticmethod
    async def delete_submenu(submenu_id: str, menu_id: str) -> bool:
        async with get_session() as db:
            submenu_to_delete = (await db.scalars(select(Submenu).where(Submenu.id == submenu_id,
                                                                        Submenu.menu_id == menu_id))).first()
            if not submenu_to_delete:
                return False
            await db.delete(submenu_to_delete)
            await db.commit()
            return True

    @staticmethod
    async def get_submenus_of_menu(menu_id: str) -> list[Submenu]:
        async with get_session() as db:
            return (await db.scalars(select(Submenu).where(Submenu.menu_id == menu_id))).all()  # type: ignore

    @staticmethod
    async def get_submenus_count(menu_id: str) -> int:
        async with get_session() as db:
            return await db.scalar(select(func.count(Submenu)).where(menu_id=menu_id))

    @staticmethod
    async def delete_submenus(submenus: set):
        async with get_session() as db:
            await db.execute(delete(Submenu).where(Submenu.id.in_(submenus)))
