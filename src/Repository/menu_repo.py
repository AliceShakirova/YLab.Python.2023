from typing import Any

from sqlalchemy import Engine, Row, func, select
from sqlalchemy.orm import Session

from src.Entities.dish import Dish
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu


class MenuRepo:

    def __init__(self, engine: Engine):
        self.engine = engine

    def create_menu(self, title: str, description: str) -> Menu:
        with Session(autoflush=False, bind=self.engine) as db:
            new_menu = Menu(title=title, description=description)
            db.add(new_menu)
            db.commit()
            db.refresh(new_menu)
            return new_menu

    def get_all_menus(self) -> list[type[Menu]]:
        with Session(autoflush=False, bind=self.engine) as db:
            all_menus = db.query(Menu).all()
            return all_menus

    def get_menu(self, menu_id: str) -> Menu | None:
        with Session(autoflush=False, bind=self.engine) as db:
            return db.query(Menu).filter_by(id=str(menu_id)).first()

    def update_menu(self, menu_id: str, title: str, description: str) -> Menu | None:
        with Session(autoflush=False, bind=self.engine) as db:
            menu_to_update = db.query(Menu).filter_by(id=str(menu_id)).first()
            if menu_to_update:
                menu_to_update.title = title
                menu_to_update.description = description
                db.commit()
                db.refresh(menu_to_update)
                return menu_to_update
            else:
                return None

    def delete_menu(self, menu_id: str) -> bool:
        with Session(autoflush=False, bind=self.engine) as db:
            menu_to_delete = db.query(Menu).filter_by(id=str(menu_id)).first()
            if not menu_to_delete:
                return False
            db.delete(menu_to_delete)
            db.commit()
            return True

    def get_submenus_and_dishes_counts(self, menu_id: str) -> Row[tuple[Any, ...] | Any]:
        with Session(autoflush=False, bind=self.engine) as db:
            return db.execute(
                select(func.count(func.distinct(Submenu.id).label('submenus_count')),
                       func.count(func.distinct(Dish.id).label('dishes_count')))
                .join(Dish, Submenu.id == Dish.submenu_id, isouter=True)
                .where(Submenu.menu_id == menu_id)
            ).first()
