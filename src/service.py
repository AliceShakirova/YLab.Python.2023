from fastapi import BackgroundTasks

from src.Cache.caches import DishCache, MenuCache, SubmenuCache, init_cache
from src.Db.database import init_db
from src.Entities.dish import Dish, DishCreateModel, DishModel
from src.Entities.menu import Menu, MenuCreateModel, MenuModel
from src.Entities.submenu import Submenu, SubmenuCreateModel, SubmenuModel
from src.Repository.dish_repo import DishRepo
from src.Repository.menu_repo import MenuRepo
from src.Repository.submenu_repo import SubmenuRepo

menu_repo = MenuRepo()
submenu_repo = SubmenuRepo()
dish_repo = DishRepo()

menu_cache = MenuCache()
submenu_cache = SubmenuCache()
dish_cache = DishCache()


async def init() -> None:
    await init_db()
    await init_cache()


async def get_all_menus_submenus_and_dishes() -> list:
    all_inst_raw = await menu_repo.get_all_menus_submenus_and_dishes()
    if all_inst_raw is None:
        return []
    else:
        all_inst = parse_all_inst(all_inst_raw)
        all_inst_ready = []
        for elem in all_inst:
            if type(elem) is Menu:
                all_inst_ready.append(MenuModel.model_validate(elem, from_attributes=True))
            elif type(elem) is Submenu:
                all_inst_ready.append(SubmenuModel.model_validate(elem, from_attributes=True))
            elif type(elem) is Dish:
                all_inst_ready.append(DishModel.model_validate(elem, from_attributes=True))
    return list(all_inst_ready)


def parse_all_inst(all_inst_raw: list) -> list:
    all_inst_raw = all_inst_raw
    all_inst = []
    last_menu = MenuModel
    last_submenu = SubmenuModel
    submenus_count, dishes_count = 0, 0
    for elem in all_inst_raw[0]:
        if type(elem) is Menu:
            if elem == last_menu:
                continue
            elem.submenus_count = submenus_count
            elem.dishes_count = dishes_count
            all_inst.append(elem)
            last_menu = elem
        elif type(elem) is Submenu:
            if elem.id == last_submenu:
                continue
            elem.dishes_count = dishes_count
            all_inst.append(elem)
            last_submenu = elem
            last_menu.submenus_count += 1
        elif type(elem) is Dish:
            all_inst.append(elem)
            last_menu.dishes_count += 1
            last_submenu.dishes_count += 1
    return all_inst


async def get_all_menus() -> list[type[Menu]] | list[MenuModel]:
    cached_all_menus = await menu_cache.get_all_menus()
    if cached_all_menus:
        return cached_all_menus

    all_menus = await menu_repo.get_all_menus()
    if all_menus is None:
        return []
    for menu in all_menus:
        menu.submenus_count, menu.dishes_count = await menu_repo.get_submenus_and_dishes_counts(menu.id)
    return all_menus


async def post_menu(menu: MenuCreateModel, background_tasks: BackgroundTasks) -> Menu:
    new_menu = await menu_repo.create_menu(title=menu.title, description=menu.description)
    new_menu.submenus_count, new_menu.dishes_count = 0, 0
    background_tasks.add_task(menu_cache.add_menu, new_menu)
    return new_menu


async def get_menu(menu_id: str) -> MenuModel | None:
    cached_menu = await menu_cache.get_menu(menu_id)
    if cached_menu is not None:
        return cached_menu
    menu = await menu_repo.get_menu(menu_id=menu_id)
    if menu is not None:
        menu.submenus_count, menu.dishes_count = await menu_repo.get_submenus_and_dishes_counts(menu_id)
    return menu


async def patch_menu(menu_id: str, menu: MenuCreateModel, background_tasks: BackgroundTasks) -> Menu | None:
    updated_menu = await menu_repo.update_menu(menu_id=menu_id, title=menu.title, description=menu.description)
    if updated_menu is None:
        return None
    updated_menu.submenus_count, updated_menu.dishes_count = await menu_repo.get_submenus_and_dishes_counts(menu_id)
    background_tasks.add_task(menu_cache.update_menu, updated_menu)
    return updated_menu


async def delete_menu(menu_id: str, background_tasks: BackgroundTasks) -> bool:
    deleted = await menu_repo.delete_menu(menu_id=menu_id)
    background_tasks.add_task(menu_cache.delete_menu, menu_id)
    return deleted


async def get_all_submenus(menu_id: str) -> list[Submenu] | list[SubmenuModel]:
    cached_submenus = await SubmenuCache.get_submenus(menu_id)
    if cached_submenus:
        return cached_submenus
    submenus = await submenu_repo.get_submenus_of_menu(menu_id)
    if not submenus:
        return []
    for submenu in submenus:
        submenu.dishes_count = await dish_repo.get_dishes_count(submenu.id)
    return submenus


async def get_submenu(menu_id: str, submenu_id: str) -> SubmenuModel | None:
    menu = await menu_cache.get_menu(menu_id)
    if menu is None:
        menu = await menu_repo.get_menu(menu_id=menu_id)
    if menu is None:
        return None
    submenu = await submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = await submenu_repo.get_submenu(menu_id, submenu_id)
    if submenu is not None:
        submenu.dishes_count = await dish_repo.get_dishes_count(submenu_id)
    return submenu


async def post_submenu(menu_id: str, submenu: SubmenuCreateModel, background_tasks: BackgroundTasks) -> Submenu:
    new_submenu = await submenu_repo.create_submenu(title=submenu.title, description=submenu.description, menu_id=menu_id)
    new_submenu.dishes_count = 0
    background_tasks.add_task(submenu_cache.add_submenu, menu_id, new_submenu)
    return new_submenu


async def patch_submenu(menu_id: str, submenu_id: str, submenu: SubmenuCreateModel,
                        background_tasks: BackgroundTasks) -> Submenu | None:
    updated_submenu = await submenu_repo.update_submenu(submenu_id=submenu_id, title=submenu.title,
                                                        description=submenu.description, menu_id=menu_id)
    if updated_submenu is None:
        return None
    updated_submenu.dishes_count = await dish_repo.get_dishes_count(updated_submenu.id)
    background_tasks.add_task(submenu_cache.update_submenu, updated_submenu)
    return updated_submenu


async def delete_submenu(menu_id: str, submenu_id: str, background_tasks: BackgroundTasks) -> bool:
    deleted = await submenu_repo.delete_submenu(submenu_id=submenu_id, menu_id=menu_id)
    background_tasks.add_task(submenu_cache.delete_submenu, menu_id, submenu_id)
    return deleted


async def get_all_dishes(menu_id: str, submenu_id: str) -> list[type[Dish]] | list[DishModel] | None:
    exist_in_cache = True
    submenu = await submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = await submenu_repo.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
        exist_in_cache = False
    if submenu is None:
        return []

    cashed_dishes = None
    if exist_in_cache:
        cashed_dishes = await dish_cache.get_dishes_of_submenu(submenu_id=submenu_id)
    if cashed_dishes is None or (exist_in_cache and len(cashed_dishes) < submenu.dishes_count):
        dishes = await dish_repo.get_dishes_of_submenu(submenu_id=submenu_id)
        if dishes is not None:
            await dish_cache.add_dishes(submenu_id, dishes)
    else:
        return cashed_dishes
    return dishes


async def get_dish(menu_id: str, submenu_id: str, dish_id: str) -> Dish | DishModel | None:
    submenu = await submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = await submenu_repo.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if submenu is None:
        return None

    dish = await dish_cache.get_dish(dish_id)
    if dish is None:
        dish = await dish_repo.get_dish(submenu_id=submenu_id, dish_id=dish_id)
    return dish


async def post_dish(menu_id: str, submenu_id: str, dish: DishCreateModel,
                    background_tasks: BackgroundTasks) -> DishModel | None:
    submenu = await submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = await submenu_repo.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return None
    new_dish = await dish_repo.create_dish(title=dish.title, description=dish.description, submenu_id=submenu_id,
                                           price=dish.price)
    background_tasks.add_task(dish_cache.add_dish, menu_id, submenu_id, new_dish)
    return new_dish


async def patch_dish(menu_id: str, submenu_id: str, dish_id: str, dish: DishCreateModel,
                     background_tasks: BackgroundTasks) -> Dish | None:
    submenu = await submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = await submenu_repo.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return None
    updated_dish = await dish_repo.update_dish(dish_id=dish_id, title=dish.title, description=dish.description,
                                               submenu_id=submenu_id, price=dish.price)
    if not updated_dish:
        return None
    background_tasks.add_task(dish_cache.update_dish, updated_dish)
    return updated_dish


async def delete_dish(menu_id: str, submenu_id: str, dish_id: str, background_tasks: BackgroundTasks) -> bool:
    submenu = await submenu_cache.get_submenu(submenu_id)
    if submenu is None:
        submenu = await submenu_repo.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return False
    deleted = await dish_repo.delete_dish(dish_id=dish_id, submenu_id=submenu_id)
    if deleted:
        background_tasks.add_task(dish_cache.delete_dish, menu_id, submenu_id, dish_id)
    return deleted
