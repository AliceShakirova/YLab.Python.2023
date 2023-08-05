import os

from src.Db.database import Database
from src.Entities.dish import Dish, DishCreateModel
from src.Entities.menu import Menu, MenuCreateModel
from src.Entities.submenu import Submenu, SubmenuCreateModel

db_address = os.getenv('db_address')
if db_address is None:
    db_address = 'localhost'

db = Database('postgres', 'qwerty', db_address, 5432, 'mydb')

repo_m = db.repo_m
repo_s = db.repo_s
repo_d = db.repo_d


def get_all_menus() -> list[type[Menu]]:
    all_menus = repo_m.get_all_menus()
    if all_menus is None:
        return []
    for menu in all_menus:
        menu.submenus_count, menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu.id)
    return all_menus


def post_menu(menu: MenuCreateModel) -> Menu:
    new_menu = repo_m.create_menu(title=menu.title, description=menu.description)
    new_menu.submenus_count, new_menu.dishes_count = 0, 0
    return new_menu


def get_menu(menu_id: str) -> Menu | None:
    menu = repo_m.get_menu(menu_id=menu_id)
    if not menu:
        return None
    menu.submenus_count, menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu_id)
    return menu


def patch_menu(menu_id: str, menu: MenuCreateModel) -> Menu | None:
    updated_menu = repo_m.update_menu(menu_id=menu_id, title=menu.title, description=menu.description)
    if updated_menu is None:
        return None
    updated_menu.submenus_count, updated_menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu_id)
    return updated_menu


def delete_menu(menu_id: str) -> bool:
    deleted = repo_m.delete_menu(menu_id=menu_id)
    if not deleted:
        return False
    else:
        return True


def get_all_submenus(menu_id: str) -> list[type[Submenu]]:
    submenus = repo_s.get_submenus_of_menu(menu_id)
    if not submenus:
        return []
    for submenu in submenus:
        submenu.dishes_count = repo_d.get_dishes_count(submenu.id)
    return submenus


def get_submenu(menu_id: str, submenu_id: str) -> Submenu | None:
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return None
    submenu.dishes_count = repo_d.get_dishes_count(submenu_id)
    return submenu


def post_submenu(menu_id: str, submenu: SubmenuCreateModel) -> Submenu:
    new_submenu = repo_s.create_submenu(title=submenu.title, description=submenu.description, menu_id=menu_id)
    new_submenu.dishes_count = 0
    return new_submenu


def patch_submenu(menu_id: str, submenu_id: str, submenu: SubmenuCreateModel) -> Submenu | None:
    updated_submenu = repo_s.update_submenu(submenu_id=submenu_id, title=submenu.title,
                                            description=submenu.description, menu_id=menu_id)
    if not updated_submenu:
        return None
    updated_submenu.dishes_count = repo_d.get_dishes_count(updated_submenu.id)
    return updated_submenu


def delete_submenu(menu_id: str, submenu_id: str) -> bool:
    deleted = repo_s.delete_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not deleted:
        return False
    else:
        return True


def get_all_dishes(menu_id: str, submenu_id: str) -> list[type[Dish]]:
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return []
    dishes = repo_d.get_dishes_of_submenu(submenu_id=submenu_id)
    return dishes


def get_dish(menu_id: str, submenu_id: str, dish_id: str) -> Dish | None:
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return None
    dish = repo_d.get_dish(submenu_id=submenu_id, dish_id=dish_id)
    if not dish:
        return None
    return dish


def post_dish(menu_id: str, submenu_id: str, dish: DishCreateModel) -> Dish | None:
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return None
    new_dish = repo_d.create_dish(title=dish.title, description=dish.description, submenu_id=submenu_id,
                                  price=dish.price)
    return new_dish


def patch_dish(menu_id: str, submenu_id: str, dish_id: str, dish: DishCreateModel) -> Dish | None:
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return None
    updated_dish = repo_d.update_dish(dish_id=dish_id, title=dish.title, description=dish.description,
                                      submenu_id=submenu_id, price=dish.price)
    if not updated_dish:
        return None
    return updated_dish


def delete_dish(menu_id: str, submenu_id: str, dish_id: str) -> bool:
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return False
    deleted = repo_d.delete_dish(dish_id=dish_id, submenu_id=submenu_id)
    if not deleted:
        return False
    else:
        return True
