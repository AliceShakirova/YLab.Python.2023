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
    #    with db.get_session() as session:
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
    def insert_inst_func(inst: Menu | Submenu | Dish, updated: bool, storage: int):
        if inst is Menu:
            test_menu = insert_menu(updated=updated, storage=storage)
            return test_menu
        if inst is Submenu:
            test_menu, test_submenu = insert_submenu(updated=updated, storage=storage)
            return test_menu, test_submenu
        if inst is Dish:
            test_menu, test_submenu, test_dish = insert_dish(updated=updated, storage=storage)
            return test_menu, test_submenu, test_dish

    yield insert_inst_func


def insert_menu(updated: bool = False, storage: int = ADD_TO_CACHE) -> Menu | MenuModel:
    if updated:
        test_menu = MenuModel().model_validate_json("{'id': '', 'title': 'My updated menu 1', 'description': 'My updated menu description 1',\
                     'submenus_count': 0, 'dishes_count': 0}")
    else:
        test_menu = MenuModel().model_validate_json("{'id': '', 'title': 'My menu 1', 'description': 'My menu description 1',\
                     'submenus_count': 0, 'dishes_count': 0}")
    if storage == NOT_ADD:
        return Menu(test_menu.title, test_menu.description)
    elif storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_menu.id = insert_menu_db(title=test_menu.title, description=test_menu.description).id
    if storage == ADD_TO_CACHE:
        insert_menu_cache(test_menu)
    return test_menu


def insert_submenu(updated: bool = False, storage: int = ADD_TO_CACHE) -> tuple[
        Menu | MenuModel, Submenu | SubmenuModel]:
    test_menu = insert_menu(updated=False, storage=ADD_TO_CACHE)
    test_menu['submenus_count'] += 1
    if updated:
        test_submenu = SubmenuModel().model_validate_json("{'id': '', 'title': 'My updated submenu 1',\
                                                          'description': 'My updated submenu description 1',\
                                                          'dishes_count': 0}")
    else:
        test_submenu = SubmenuModel().model_validate_json("{'id': '', 'title': 'My submenu 1',"
                                                          "'description': 'My submenu description 1',\
                                                          'dishes_count': 0}")
    if storage == NOT_ADD:
        return test_menu, test_submenu
    elif storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_submenu['id'] = insert_submenu_db(title=str(test_submenu['title']),
                                               description=str(test_submenu['description']), menu_id=test_menu['id']).id
    if storage == ADD_TO_CACHE:
        insert_submenu_cache(submenu_id=test_submenu['id'], title=str(test_submenu['title']),
                             description=str(test_submenu['description']), menu_id=test_menu['id'],
                             dishes_count=int(test_submenu['dishes_count']))
    return test_menu, test_submenu


def insert_dish(updated: bool = False,
                storage: int = ADD_TO_CACHE) -> tuple[Menu | MenuModel, Submenu | SubmenuModel, Dish | DishModel]:
    test_menu, test_submenu = insert_submenu(updated=updated, storage=ADD_TO_CACHE)
    test_menu['dishes_count'] += 1
    test_submenu['dishes_count'] += 1
    if updated:
        test_dish = DishModel.model_validate_json("{'id': '', 'title': 'My updated dish 1',\
        'description': 'My updated dish description 1', 'price': '14.50'}")
    else:
        test_dish = DishModel.model_validate_json("{'id': '', 'title': 'My dish 1',\
        'description': 'My dish description 1', 'price': '12.50'}")
    if storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_dish['id'] = insert_dish_db(title=str(test_dish['title']), description=str(test_dish['description']),
                                         submenu_id=str(test_submenu['id']), price=Decimal(test_dish['price'])).id
    if storage == ADD_TO_CACHE:
        insert_dish_cache(dish_id=test_dish['id'], title=str(test_dish['title']),
                          description=str(test_dish['description']), menu_id=test_menu['id'],
                          submenu_id=str(test_submenu['id']), price=Decimal(test_dish['price']))
    return test_menu, test_submenu, test_dish


def func_reverse(function: str, **kwargs) -> str:
    return app.url_path_for(function, **kwargs)
