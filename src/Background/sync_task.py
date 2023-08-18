import asyncio

import openpyxl
from _pydecimal import Decimal
from openpyxl import load_workbook
from openpyxl.cell import Cell
from openpyxl.workbook import Workbook

from src.Cache.caches import DishCache, MenuCache, SubmenuCache, clear_cache, init_cache
from src.celery_worker import celery_app
from src.Db.database import init_db
from src.Entities.dish import Dish
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu
from src.Repository import dish_repo as dr
from src.Repository import menu_repo as mr
from src.Repository import submenu_repo as sr
from src.Repository.dish_repo import DishRepo
from src.Repository.menu_repo import MenuRepo
from src.Repository.submenu_repo import SubmenuRepo

menu_repo: MenuRepo = mr.MenuRepo()
submenu_repo: SubmenuRepo = sr.SubmenuRepo()
dish_repo: DishRepo = dr.DishRepo()

menu_cache: MenuCache = MenuCache()
submenu_cache: SubmenuCache = SubmenuCache()
dish_cache: DishCache = DishCache()

filename: str = 'admin/Menu.xlsx'


@celery_app.task
def sync_task() -> None:
    loop = asyncio.new_event_loop()
    loop.run_until_complete(update_from_excel())


async def update_from_excel() -> None:
    await init_db()
    await init_cache()
    wb: openpyxl.Workbook = load_workbook(filename=filename)  # type: ignore
    data = await menu_repo.get_full_tree()
    tree: dict = {}

    list(map(lambda menu: process_item(menu, tree), data))

    await process_menus(wb, tree)


def process_item(item: Menu | Submenu | Dish, tree: dict) -> None:
    tree[item.id] = item
    if type(item) is Menu:
        item.submenu_tree = {}
        list(map(lambda submenu: process_item(submenu, item.submenu_tree), item.submenus))
    elif type(item) is Submenu:
        item.dish_tree = {}
        list(map(lambda dish: process_item(dish, item.dish_tree), item.dishes))


async def process_menus(wb: Workbook, db_data: dict[str, Menu]) -> None:
    current_menu_id: str = ''
    current_submenu_id: str = ''

    menus_in_excel: set[str] = set()
    submenus_in_excel: set[str] = set()
    dishes_in_excel: set[str] = set()

    await clear_cache()

    for row in wb.worksheets[0].rows:
        if row[0].value is not None:
            menu = process_menu(row)
            current_menu_id = menu.id
            menus_in_excel.add(menu.id)
            found_menu = db_data.get(menu.id)

            if found_menu is None:
                await menu_repo.create_menu_from_object(menu)
                await menu_cache.add_menu(menu)
            elif found_menu != menu:
                await menu_repo.update_menu_from_object(menu)
                await menu_cache.update_menu(menu)

        elif row[1].value is not None:
            submenu = process_submenu(row, current_menu_id)
            current_submenu_id = submenu.id
            submenus_in_excel.add(submenu.id)
            try:
                found_submenu = db_data.get(current_menu_id).submenu_tree.get(submenu.id)  # type: ignore
            except AttributeError:
                found_submenu = None

            if found_submenu is None:
                await submenu_repo.create_submenu_from_object(submenu)
                await submenu_cache.add_submenu(submenu)
            elif found_submenu != submenu:
                await submenu_repo.update_submenu_from_object(submenu)
                await submenu_cache.update_submenu(submenu)

        elif row[2].value is not None:
            dish = process_dish(row, current_submenu_id)
            dishes_in_excel.add(dish.id)
            try:
                found_dish = (db_data.get(current_menu_id)
                              .submenu_tree.get(current_submenu_id).dish_tree.get(dish.id))  # type: ignore
            except AttributeError:
                found_dish = None

            if found_dish is None:
                await dish_repo.create_dish_from_object(dish)
                await dish_cache.add_dish(current_menu_id, dish)
            elif found_dish != dish:
                await dish_repo.update_dish_from_object(dish)
                await dish_cache.update_dish(dish)

    menus_in_db: set[str] = set()
    submenus_in_db: set[str] = set()
    dishes_in_db: set[str] = set()

    for menu in db_data.values():
        menus_in_db.add(menu.id)
        for submenu in menu.submenu_tree.values():  # type: ignore
            submenus_in_db.add(submenu.id)
            dishes_in_db.union(submenu.dish_tree.keys())

    menus_to_delete = menus_in_db - menus_in_excel
    submenus_to_delete = submenus_in_db - submenus_in_excel
    dishes_to_delete = dishes_in_db - dishes_in_excel

    await menu_repo.delete_menus(menus_to_delete)
    await submenu_repo.delete_submenus(submenus_to_delete)
    await dish_repo.delete_dishes(dishes_to_delete)


def process_menu(row: tuple[Cell, ...]) -> Menu:
    menu_id: str = row[0].value
    menu_title: str = row[1].value
    menu_description: str = row[2].value
    return Menu(menu_title, menu_description, menu_id)


def process_submenu(row: tuple[Cell, ...], menu_id: str) -> Submenu:
    submenu_id: str = row[1].value
    submenu_title: str = row[2].value
    submenu_description: str = row[3].value
    return Submenu(submenu_title, submenu_description, menu_id, submenu_id)


def process_dish(row: tuple[Cell, ...], submenu_id: str) -> Dish:
    dish_id: str = row[2].value
    dish_title: str = row[3].value
    dish_description: str = row[4].value
    dish_price: Decimal = row[5].value
    return Dish(dish_title, dish_description, submenu_id, dish_price, dish_id)


if __name__ == '__main__':
    filename = '../../admin/Menu.xlsx'
    loop = asyncio.new_event_loop()
    loop.run_until_complete(update_from_excel())
