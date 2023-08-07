import pytest
from _pydecimal import Decimal
from sqlalchemy import text

from src.app import app
from src.Cache.caches import DishCache, MenuCache, SubmenuCache, redisCache
from src.Entities.dish import Dish, DishModel
from src.Entities.menu import Menu, MenuModel
from src.Entities.submenu import Submenu, SubmenuModel
from src.service import db


@pytest.fixture
def clear_storage():
    def clear_storage_func():
        with db.get_session() as session:
            session.execute(text(f'TRUNCATE {Menu.__tablename__} CASCADE'))
            session.commit()
        redisCache.flushdb(asynchronous=False)

    yield clear_storage_func
    clear_storage_func()


@pytest.fixture
def start_clear_storage():
    def start_clear_storage_func():
        with db.get_session() as session:
            session.execute(text(f'TRUNCATE {Menu.__tablename__} CASCADE'))
            session.commit()
            redisCache.flushdb(asynchronous=False)

    yield start_clear_storage_func


@pytest.fixture
def insert_menu():
    def insert_menu_func(title: str, description: str) -> Menu:
        menu = Menu(title=title, description=description)
        session.add(menu)
        session.commit()
        session.refresh(menu)
        return menu

    with db.get_session() as session:
        yield insert_menu_func


@pytest.fixture
def insert_menu_cache():
    def insert_menu_cache_func(menu_id: str, title: str, description: str, submenus_count: int,
                               dishes_count: int) -> MenuModel:
        menu = Menu(title=title, description=description)
        menu.submenus_count, menu.dishes_count = submenus_count, dishes_count
        menu.id = menu_id
        return MenuCache.add_menu(menu)
    yield insert_menu_cache_func


@pytest.fixture
def insert_submenu():
    def insert_submenu_func(title: str, description: str, menu_id: str) -> Submenu:
        submenu = Submenu(title=title, description=description, menu_id=menu_id)
        session.add(submenu)
        session.commit()
        session.refresh(submenu)
        return submenu

    with db.get_session() as session:
        yield insert_submenu_func


@pytest.fixture
def insert_submenu_cache():
    def insert_submenu_cache_func(submenu_id: str, title: str, description: str, dishes_count: int,
                                  menu_id: str) -> SubmenuModel:
        submenu = Submenu(title=title, description=description, menu_id=menu_id)
        submenu.dishes_count = dishes_count
        submenu.id = submenu_id
        return SubmenuCache.add_submenu(menu_id=menu_id, submenu=submenu)
    yield insert_submenu_cache_func


@pytest.fixture
def insert_dish():
    def insert_dish_func(title: str, description: str, submenu_id: str, price: Decimal) -> Dish:
        dish = Dish(title=title, description=description, submenu_id=submenu_id, price=price)
        session.add(dish)
        session.commit()
        session.refresh(dish)

        dish_model: DishModel = DishModel.model_validate(dish)
        redisCache.set(dish.id, dish_model.model_dump_json())

        return dish

    with db.get_session() as session:
        yield insert_dish_func


@pytest.fixture
def insert_dish_cache():
    def insert_dish_cache_func(dish_id: str, title: str, description: str, price: Decimal, menu_id: str, submenu_id: str) -> DishModel:
        dish = Dish(title=title, description=description, submenu_id=submenu_id, price=price)
        dish.id = dish_id
        return DishCache.add_dish(menu_id=menu_id, submenu_id=submenu_id, dish=dish)
    yield insert_dish_cache_func


def func_reverse(function: str, **kwargs) -> str:
    return app.url_path_for(function, **kwargs)
