from src.Cache.caches import DishCache, MenuCache, SubmenuCache
from src.Db.database import Database
from src.Entities.dish import Dish, DishCreateModel, DishModel
from src.Entities.menu import Menu, MenuCreateModel, MenuModel
from src.Entities.submenu import Submenu, SubmenuCreateModel, SubmenuModel

db = Database()
repo_m = db.repo_m
repo_s = db.repo_s
repo_d = db.repo_d

menu_cache = MenuCache()
submenu_cache = SubmenuCache()
dish_cache = DishCache()


def get_all_menus() -> list[type[Menu]] | list[MenuModel]:
    cached_all_menus = MenuCache.get_all_menus()
    if cached_all_menus:
        return cached_all_menus

    all_menus = repo_m.get_all_menus()
    if all_menus is None:
        return []
    for menu in all_menus:
        menu.submenus_count, menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu.id)
    return all_menus


def post_menu(menu: MenuCreateModel) -> MenuModel:
    new_menu = repo_m.create_menu(title=menu.title, description=menu.description)
    new_menu.submenus_count, new_menu.dishes_count = 0, 0
    return menu_cache.add_menu(new_menu)


def get_menu(menu_id: str) -> MenuModel | None:
    cached_menu = menu_cache.get_menu(menu_id)
    if cached_menu is not None:
        return cached_menu
    menu = repo_m.get_menu(menu_id=menu_id)
    if menu is not None:
        menu.submenus_count, menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu_id)
    return menu


def patch_menu(menu_id: str, menu: MenuCreateModel) -> MenuModel | None:
    updated_menu = repo_m.update_menu(menu_id=menu_id, title=menu.title, description=menu.description)
    if updated_menu is None:
        return None
    updated_menu.submenus_count, updated_menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu_id)
    return menu_cache.update_menu(updated_menu)


def delete_menu(menu_id: str) -> bool:
    deleted = repo_m.delete_menu(menu_id=menu_id)
    menu_cache.delete_menu(menu_id)
    return deleted


def get_all_submenus(menu_id: str) -> list[Submenu] | list[SubmenuModel]:
    cached_submenus = SubmenuCache.get_submenus(menu_id)
    if cached_submenus:
        return cached_submenus
    submenus = repo_s.get_submenus_of_menu(menu_id)
    if not submenus:
        return []
    for submenu in submenus:
        submenu.dishes_count = repo_d.get_dishes_count(submenu.id)
    return submenus


def get_submenu(menu_id: str, submenu_id: str) -> SubmenuModel | None:
    menu = menu_cache.get_menu(menu_id)
    if menu is None:
        menu = repo_m.get_menu(menu_id=menu_id)
    if menu is None:
        return None
    submenu = submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = repo_s.get_submenu(menu_id, submenu_id)
    if submenu is not None:
        submenu.dishes_count = repo_d.get_dishes_count(submenu_id)
    return submenu


def post_submenu(menu_id: str, submenu: SubmenuCreateModel) -> SubmenuModel:
    new_submenu = repo_s.create_submenu(title=submenu.title, description=submenu.description, menu_id=menu_id)
    new_submenu.dishes_count = 0
    return submenu_cache.add_submenu(menu_id, new_submenu)


def patch_submenu(menu_id: str, submenu_id: str, submenu: SubmenuCreateModel) -> SubmenuModel | None:
    updated_submenu = repo_s.update_submenu(submenu_id=submenu_id, title=submenu.title,
                                            description=submenu.description, menu_id=menu_id)
    if updated_submenu is None:
        return None
    updated_submenu.dishes_count = repo_d.get_dishes_count(updated_submenu.id)
    return submenu_cache.update_submenu(updated_submenu)


def delete_submenu(menu_id: str, submenu_id: str) -> bool:
    deleted = repo_s.delete_submenu(submenu_id=submenu_id, menu_id=menu_id)
    submenu_cache.delete_submenu(menu_id, submenu_id)
    return deleted


def get_all_dishes(menu_id: str, submenu_id: str) -> list[type[Dish]] | list[DishModel] | None:
    exist_in_cache = True
    submenu = submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
        exist_in_cache = False
    if submenu is None:
        return []

    cashed_dishes = None
    if exist_in_cache:
        cashed_dishes = dish_cache.get_dishes_of_submenu(submenu_id=submenu_id)
    if cashed_dishes is None or (exist_in_cache and len(cashed_dishes) < submenu.dishes_count):
        dishes = repo_d.get_dishes_of_submenu(submenu_id=submenu_id)
        if dishes is not None:
            dish_cache.add_dishes(submenu_id, dishes)
    else:
        return cashed_dishes
    return dishes


def get_dish(menu_id: str, submenu_id: str, dish_id: str) -> Dish | DishModel | None:
    submenu = submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if submenu is None:
        return None

    dish = dish_cache.get_dish(dish_id)
    if dish is None:
        dish = repo_d.get_dish(submenu_id=submenu_id, dish_id=dish_id)
    return dish


def post_dish(menu_id: str, submenu_id: str, dish: DishCreateModel) -> DishModel | None:
    submenu = submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return None
    new_dish = repo_d.create_dish(title=dish.title, description=dish.description, submenu_id=submenu_id,
                                  price=dish.price)
    return dish_cache.add_dish(menu_id, submenu_id, new_dish)


def patch_dish(menu_id: str, submenu_id: str, dish_id: str, dish: DishCreateModel) -> DishModel | None:
    submenu = submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return None
    updated_dish = repo_d.update_dish(dish_id=dish_id, title=dish.title, description=dish.description,
                                      submenu_id=submenu_id, price=dish.price)
    if not updated_dish:
        return None
    return dish_cache.update_dish(updated_dish)


def delete_dish(menu_id: str, submenu_id: str, dish_id: str) -> bool:
    submenu = submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return False
    dish_cache.delete_dish(menu_id, submenu_id, dish_id)
    deleted = repo_d.delete_dish(dish_id=dish_id, submenu_id=submenu_id)
    return deleted
