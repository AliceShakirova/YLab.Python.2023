import pytest
from _pydecimal import Decimal
from sqlalchemy import text

from src.app import app
from src.Cache.caches import DishCache, MenuCache, SubmenuCache, redisCache
from src.Entities.dish import Dish, DishModel
from src.Entities.menu import Menu, MenuModel
from src.Entities.submenu import Submenu, SubmenuModel
from src.service import db

NOT_ADD = 0
ADD_TO_DB = 1
ADD_TO_CACHE = 2


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


def insert_menu_db(title: str, description: str) -> Menu:
    with db.get_session() as session:
        menu = Menu(title=title, description=description)
        session.add(menu)
        session.commit()
        session.refresh(menu)
        return menu


def insert_menu_cache(menu_model: MenuModel) -> MenuModel:
    menu = Menu(title=menu_model.title, description=menu_model.description)
    menu.submenus_count, menu.dishes_count = menu_model.submenus_count, menu_model.dishes_count
    menu.id = menu_model.id
    return MenuCache.add_menu(menu)


def insert_submenu_db(title: str, description: str, menu_id: str) -> Submenu:
    with db.get_session() as session:
        submenu = Submenu(title=title, description=description, menu_id=menu_id)
        session.add(submenu)
        session.commit()
        session.refresh(submenu)
        return submenu


def insert_submenu_cache(submenu_id: str, title: str, description: str, dishes_count: int,
                         menu_id: str) -> SubmenuModel:
    submenu = Submenu(title=title, description=description, menu_id=menu_id)
    submenu.dishes_count = dishes_count
    submenu.id = submenu_id
    return SubmenuCache.add_submenu(menu_id=menu_id, submenu=submenu)


def insert_dish_db(title: str, description: str, submenu_id: str, price: Decimal) -> Dish:
    with db.get_session() as session:
        dish = Dish(title=title, description=description, submenu_id=submenu_id, price=price)
        session.add(dish)
        session.commit()
        session.refresh(dish)
        return dish


def insert_dish_cache(dish_id: str, title: str, description: str, price: Decimal, menu_id: str,
                      submenu_id: str) -> DishModel:
    dish = Dish(title=title, description=description, submenu_id=submenu_id, price=price)
    dish.id = dish_id
    return DishCache.add_dish(menu_id=menu_id, submenu_id=submenu_id, dish=dish)


@pytest.fixture
def insert_inst():
    def insert_inst_func(inst: Menu | Submenu | Dish, storage: int):
        if inst is Menu:
            test_menu = insert_menu(storage=storage)
            return test_menu
        if inst is Submenu:
            test_menu, test_submenu = insert_submenu(storage=storage)
            return test_menu, test_submenu
        if inst is Dish:
            test_menu, test_submenu, test_dish = insert_dish(storage=storage)
            return test_menu, test_submenu, test_dish

    yield insert_inst_func


def insert_menu(storage: int = ADD_TO_CACHE) -> Menu | MenuModel:
    menu = Menu('My menu 1', 'My menu description 1')
    menu.submenus_count, menu.dishes_count = 0, 0
    test_menu: MenuModel = MenuModel.model_validate(menu, from_attributes=True)
    if storage == NOT_ADD:
        return test_menu
    elif storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_menu.id = insert_menu_db(title=test_menu.title, description=test_menu.description).id
    if storage == ADD_TO_CACHE:
        insert_menu_cache(test_menu)
    return test_menu


def insert_submenu(storage: int = ADD_TO_CACHE) -> tuple[
        Menu | MenuModel, Submenu | SubmenuModel]:
    test_menu = insert_menu(storage=ADD_TO_CACHE)
    test_menu.submenus_count += 1
    submenu = Submenu('My submenu 1', 'My submenu description 1', test_menu.id)
    submenu.dishes_count = 0
    test_submenu: SubmenuModel = SubmenuModel.model_validate(submenu, from_attributes=True)
    if storage == NOT_ADD:
        return test_menu, test_submenu
    elif storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_submenu.id = insert_submenu_db(title=str(test_submenu.title),
                                            description=str(test_submenu.description), menu_id=test_menu.id).id
    if storage == ADD_TO_CACHE:
        insert_submenu_cache(submenu_id=test_submenu.id, title=str(test_submenu.title),
                             description=str(test_submenu.description), menu_id=test_menu.id,
                             dishes_count=int(test_submenu.dishes_count))
    return test_menu, test_submenu


def insert_dish(storage: int = ADD_TO_CACHE) -> tuple[Menu | MenuModel, Submenu | SubmenuModel, Dish | DishModel]:
    test_menu, test_submenu = insert_submenu(storage=ADD_TO_CACHE)
    test_menu.dishes_count += 1
    test_submenu.dishes_count += 1
    dish = Dish('My dish 1', 'My dish description 1', test_submenu.id, Decimal(12.50))
    test_dish: DishModel = DishModel.model_validate(dish, from_attributes=True)
    if storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_dish.id = insert_dish_db(title=str(test_dish.title), description=str(test_dish.description),
                                      submenu_id=str(test_submenu.id), price=Decimal(test_dish.price)).id
    if storage == ADD_TO_CACHE:
        insert_dish_cache(dish_id=test_dish.id, title=str(test_dish.title),
                          description=str(test_dish.description), menu_id=test_menu.id,
                          submenu_id=str(test_submenu.id), price=Decimal(test_dish.price))
    return test_menu, test_submenu, test_dish


def func_reverse(function: str, **kwargs) -> str:
    return app.url_path_for(function, **kwargs)
