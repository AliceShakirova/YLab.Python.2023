import pytest
from sqlalchemy import text

from src.app import app
from src.Entities.dish import Dish
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu
from src.service import db


@pytest.fixture
def clear_db():
    def clear_db_func():
        with db.get_session() as session:
            session.execute(text(f'TRUNCATE {Menu.__tablename__} CASCADE'))
            session.commit()

    yield clear_db_func
    clear_db_func()


@pytest.fixture
def start_clear_db():
    def start_clear_db_func():
        with db.get_session() as session:
            session.execute(text(f'TRUNCATE {Menu.__tablename__} CASCADE'))
            session.commit()

    yield start_clear_db_func


@pytest.fixture
def insert_menu():
    def insert_menu_func(title, desc):
        menu = Menu(title=title, description=desc)
        session.add(menu)
        session.commit()
        session.refresh(menu)
        return menu

    with db.get_session() as session:
        yield insert_menu_func


@pytest.fixture
def insert_submenu():
    def insert_submenu_func(title, desc, menu_id):
        submenu = Submenu(title=title, description=desc, menu_id=menu_id)
        session.add(submenu)
        session.commit()
        session.refresh(submenu)
        return submenu

    with db.get_session() as session:
        yield insert_submenu_func


@pytest.fixture
def insert_dish():
    def insert_dish_func(title, desc, submenu_id, price):
        dish = Dish(title=title, description=desc, submenu_id=submenu_id, price=price)
        session.add(dish)
        session.commit()
        session.refresh(dish)
        return dish

    with db.get_session() as session:
        yield insert_dish_func


def func_reverse(function: str, **kwargs):
    return app.url_path_for(function, **kwargs)
