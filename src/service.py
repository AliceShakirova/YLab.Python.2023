import os

from src.Db.database import Database

db_address = os.getenv('db_address')
if db_address is None:
    db_address = 'localhost'

db = Database('postgres', 'qwerty', db_address, 5432, 'mydb')

repo_m = db.repo_m
repo_s = db.repo_s
repo_d = db.repo_d


def get_all_menus():
    all_menus = repo_m.get_all_menus()
    if not all_menus:
        return []
    for menu in all_menus:
        menu.submenus_count, menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu.id)
    return all_menus


def post_menu(menu):
    new_menu = repo_m.create_menu(title=menu.title, description=menu.description)
    new_menu.submenus_count, new_menu.dishes_count = 0, 0
    return new_menu


def get_menu(menu_id):
    menu = repo_m.get_menu(menu_id=menu_id)
    if not menu:
        return False
    menu.submenus_count, menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu.id)
    return menu


def patch_menu(menu_id, menu):
    updated_menu = repo_m.update_menu(menu_id=menu_id, title=menu.title, description=menu.description)
    if not updated_menu:
        return False
    updated_menu.submenus_count, updated_menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu.id)
    return updated_menu


def delete_menu(menu_id):
    deleted = repo_m.delete_menu(menu_id=menu_id)
    if not deleted:
        return False
    else:
        return True


def get_all_submenus(menu_id):
    submenus = repo_s.get_submenus_of_menu(menu_id)
    if not submenus:
        return []
    for submenu in submenus:
        submenu.dishes_count = repo_d.get_dishes_count(submenu.id)
    return submenus


def get_submenu(menu_id, submenu_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return False
    submenu.dishes_count = repo_d.get_dishes_count(submenu.id)
    return submenu


def post_submenu(menu_id, submenu):
    new_submenu = repo_s.create_submenu(title=submenu.title, description=submenu.description, menu_id=menu_id)
    new_submenu.dishes_count = 0
    return new_submenu


def patch_submenu(menu_id, submenu_id, submenu):
    updated_submenu = repo_s.update_submenu(submenu_id=submenu_id, title=submenu.title,
                                            description=submenu.description, menu_id=menu_id)
    if not updated_submenu:
        return False
    updated_submenu.dishes_count = repo_d.get_dishes_count(updated_submenu.id)
    return updated_submenu


def delete_submenu(menu_id, submenu_id):
    deleted = repo_s.delete_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not deleted:
        return False
    else:
        return True


def get_all_dishes(menu_id, submenu_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return []
    dishes = repo_d.get_dishes_of_submenu(submenu_id=submenu_id)
    return dishes


def get_dish(menu_id, submenu_id, dish_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return False
    dish = repo_d.get_dish(submenu_id=submenu_id, dish_id=dish_id)
    if not dish:
        return False
    return dish


def post_dish(menu_id, submenu_id, dish):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return False
    new_dish = repo_d.create_dish(title=dish.title, description=dish.description, submenu_id=submenu_id,
                                  price=dish.price)
    return new_dish


def patch_dish(menu_id, submenu_id, dish_id, dish):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return False
    updated_dish = repo_d.update_dish(dish_id=dish_id, title=dish.title, description=dish.description,
                                      submenu_id=submenu_id, price=dish.price)
    if not updated_dish:
        return False
    return updated_dish


def delete_dish(menu_id, submenu_id, dish_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return False
    deleted = repo_d.delete_dish(dish_id=dish_id, submenu_id=submenu_id)
    if not deleted:
        return False
    else:
        return True
