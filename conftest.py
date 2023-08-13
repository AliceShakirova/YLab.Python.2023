import asyncio
from typing import AsyncGenerator

import pytest
from _pydecimal import Decimal
from sqlalchemy import text

from src.app import app
from src.Cache.caches import DishCache, MenuCache, SubmenuCache, get_redis, init_cache
from src.Db.database import get_session, init_db
from src.Entities.dish import Dish, DishModel
from src.Entities.menu import Menu, MenuModel
from src.Entities.submenu import Submenu, SubmenuModel

NOT_ADD = 0
ADD_TO_DB = 1
ADD_TO_CACHE = 2


@pytest.fixture(scope='session')
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def init():
    init_db()
    init_cache()


@pytest.fixture
async def clear_storage() -> AsyncGenerator | None:
    async def clear_storage_func():
        async with get_session() as session:
            await session.execute(text(f'TRUNCATE {Menu.__tablename__} CASCADE'))
            await session.commit()
        async with get_redis() as redis:
            await redis.flushdb()

    yield clear_storage_func
    await clear_storage_func()


@pytest.fixture()
async def start_clear_storage():
    async with get_session() as session:
        await session.execute(text(f'TRUNCATE {Menu.__tablename__} CASCADE'))
        await session.commit()
    async with get_redis() as redis:
        await redis.flushdb()


async def insert_menu_db(title: str, description: str) -> Menu:
    async with get_session() as session:
        menu = Menu(title=title, description=description)
        session.add(menu)
        await session.commit()
        await session.refresh(menu)
        return menu


async def insert_menu_cache(menu_model: MenuModel) -> MenuModel:
    menu = Menu(title=menu_model.title, description=menu_model.description)
    menu.submenus_count, menu.dishes_count = menu_model.submenus_count, menu_model.dishes_count
    menu.id = menu_model.id
    return await MenuCache.add_menu(menu)


async def insert_submenu_db(title: str, description: str, menu_id: str) -> Submenu:
    async with get_session() as session:
        submenu = Submenu(title=title, description=description, menu_id=menu_id)
        session.add(submenu)
        await session.commit()
        await session.refresh(submenu)
        return submenu


async def insert_submenu_cache(submenu_id: str, title: str, description: str, dishes_count: int,
                               menu_id: str) -> SubmenuModel:
    submenu = Submenu(title=title, description=description, menu_id=menu_id)
    submenu.dishes_count = dishes_count
    submenu.id = submenu_id
    return await SubmenuCache.add_submenu(menu_id=menu_id, submenu=submenu)


async def insert_dish_db(title: str, description: str, submenu_id: str, price: Decimal) -> Dish:
    async with get_session() as session:
        dish = Dish(title=title, description=description, submenu_id=submenu_id, price=price)
        session.add(dish)
        await session.commit()
        await session.refresh(dish)
        return dish


async def insert_dish_cache(dish_id: str, title: str, description: str, price: Decimal, menu_id: str,
                            submenu_id: str) -> DishModel:
    dish = Dish(title=title, description=description, submenu_id=submenu_id, price=price)
    dish.id = dish_id
    return await DishCache.add_dish(menu_id=menu_id, submenu_id=submenu_id, dish=dish)


@pytest.fixture
def insert_inst():
    async def insert_inst_func(inst: Menu | Submenu | Dish, storage: int):
        if inst is Menu:
            test_menu = await insert_menu(storage=storage)
            return test_menu
        if inst is Submenu:
            test_menu, test_submenu = await insert_submenu(storage=storage)
            return test_menu, test_submenu
        if inst is Dish:
            test_menu, test_submenu, test_dish = await insert_dish(storage=storage)
            return test_menu, test_submenu, test_dish

    yield insert_inst_func


async def insert_menu(storage: int = ADD_TO_CACHE) -> Menu | MenuModel:
    menu = Menu('My menu 1', 'My menu description 1')
    menu.submenus_count, menu.dishes_count = 0, 0
    test_menu: MenuModel = MenuModel.model_validate(menu, from_attributes=True)
    if storage == NOT_ADD:
        return test_menu
    elif storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_menu.id = (await insert_menu_db(title=test_menu.title, description=test_menu.description)).id
    if storage == ADD_TO_CACHE:
        await insert_menu_cache(test_menu)
    return test_menu


async def insert_submenu(storage: int = ADD_TO_CACHE) -> tuple[
        Menu | MenuModel, Submenu | SubmenuModel]:
    test_menu = await insert_menu(storage=ADD_TO_CACHE)
    test_menu.submenus_count += 1
    submenu = Submenu('My submenu 1', 'My submenu description 1', test_menu.id)
    submenu.dishes_count = 0
    test_submenu: SubmenuModel = SubmenuModel.model_validate(submenu, from_attributes=True)
    if storage == NOT_ADD:
        return test_menu, test_submenu
    elif storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_submenu.id = (await insert_submenu_db(title=str(test_submenu.title),
                                                   description=str(test_submenu.description), menu_id=test_menu.id)).id
    if storage == ADD_TO_CACHE:
        await insert_submenu_cache(submenu_id=test_submenu.id, title=str(test_submenu.title),
                                   description=str(test_submenu.description), menu_id=test_menu.id,
                                   dishes_count=int(test_submenu.dishes_count))
    return test_menu, test_submenu


async def insert_dish(storage: int = ADD_TO_CACHE) -> tuple[Menu | MenuModel, Submenu | SubmenuModel, Dish | DishModel]:
    test_menu, test_submenu = await insert_submenu(storage=ADD_TO_CACHE)
    test_menu.dishes_count += 1
    test_submenu.dishes_count += 1
    dish = Dish('My dish 1', 'My dish description 1', test_submenu.id, Decimal(12.50))
    test_dish: DishModel = DishModel.model_validate(dish, from_attributes=True)
    if storage == ADD_TO_DB or storage == ADD_TO_CACHE:
        test_dish.id = (await insert_dish_db(title=str(test_dish.title), description=str(test_dish.description),
                                             submenu_id=str(test_submenu.id), price=Decimal(test_dish.price))).id
    if storage == ADD_TO_CACHE:
        await insert_dish_cache(dish_id=test_dish.id, title=str(test_dish.title),
                                description=str(test_dish.description), menu_id=test_menu.id,
                                submenu_id=str(test_submenu.id), price=Decimal(test_dish.price))
    return test_menu, test_submenu, test_dish


def func_reverse(function: str, **kwargs) -> str:
    return app.url_path_for(function, **kwargs)
