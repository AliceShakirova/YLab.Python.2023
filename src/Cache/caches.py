import json
from os import getenv

import redis
from pydantic import TypeAdapter
from redis.client import Pipeline

from src.Cache import cache_settings
from src.Entities.dish import Dish, DishModel
from src.Entities.menu import Menu, MenuModel
from src.Entities.submenu import Submenu, SubmenuModel

dish_ids_type_adapter = TypeAdapter(list[str])
dish_list_type_adapter = TypeAdapter(list[DishModel])

conn_str = getenv('REDIS_OM_URL')
if conn_str is not None:
    redisCache = redis.from_url(conn_str, decode_responses=True)
else:
    redisCache = redis.Redis(host='localhost', port=6379, decode_responses=True)


class MenuCache:
    all_menus_key = 'all_menus'

    def __init__(self):
        pass

    @classmethod
    def get_all_menus(cls) -> list[MenuModel]:
        all_menu_ids = MenuCache.get_all_menu_ids()
        if len(all_menu_ids) == 0:
            return []
        result = []
        all_menus_raw = redisCache.mget(all_menu_ids)
        for menu_raw in all_menus_raw:
            model: MenuModel = MenuModel.model_validate_json(menu_raw)
            result.append(model)
        return result

    @classmethod
    def add_menu(cls, menu: Menu) -> MenuModel:
        model: MenuModel = MenuModel.model_validate(menu, from_attributes=True)
        redisCache.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        menu_ids = MenuCache.get_all_menu_ids()
        menu_ids.add(model.id)
        MenuCache.save_all_menu_ids(menu_ids)
        return model

    @classmethod
    def get_menu(cls, menu_id: str) -> MenuModel | None:
        menu_raw = redisCache.get(menu_id)
        if menu_raw is None:
            return None
        return MenuModel.model_validate_json(menu_raw)

    @classmethod
    def update_menu(cls, menu: Menu) -> MenuModel:
        model: MenuModel = MenuModel.model_validate(menu, from_attributes=True)
        redisCache.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        return model

    @classmethod
    def delete_menu(cls, menu_id: str):
        pipe = redisCache.pipeline()
        pipe.delete(menu_id)
        menu_ids = MenuCache.get_all_menu_ids()
        menu_ids.discard(menu_id)
        MenuCache.save_all_menu_ids(menu_ids, pipe)
        SubmenuCache.delete_all_submenus(menu_id, pipe)
        pipe.execute()

    @classmethod
    def get_all_menu_ids(cls) -> set[str]:
        menu_ids_raw = redisCache.get(cls.all_menus_key)
        if menu_ids_raw is None:
            return set()
        menu_ids = set(json.loads(menu_ids_raw.replace("'", '"')))
        return menu_ids

    @classmethod
    def save_all_menu_ids(cls, menu_ids: set[str], pipe: Pipeline | None = None):
        if pipe:
            pipe.set(cls.all_menus_key, json.dumps(list(menu_ids)), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        else:
            redisCache.set(cls.all_menus_key, json.dumps(list(menu_ids)), ex=cache_settings.CACHE_EXPIRE_SECONDS)


class SubmenuCache:
    SUBMENUS_KEY_FORMAT = '{0}_submenus'

    def __init__(self):
        pass

    @classmethod
    def get_submenus(cls, menu_id: str) -> list[SubmenuModel]:
        submenu_ids = SubmenuCache.get_submenu_ids(menu_id)
        if not submenu_ids:
            return []
        submenus_raw = redisCache.mget(submenu_ids)
        if submenus_raw is None or submenus_raw == []:
            return []
        result = []
        for submenu_raw in submenus_raw:
            submenu: SubmenuModel = SubmenuModel.model_validate_json(submenu_raw)
            result.append(submenu)
        return result

    @classmethod
    def add_submenu(cls, menu_id: str, submenu: Submenu) -> SubmenuModel:
        model: SubmenuModel = SubmenuModel.model_validate(submenu, from_attributes=True)
        redisCache.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        submenu_ids = SubmenuCache.get_submenu_ids(menu_id)
        submenu_ids.add(model.id)
        SubmenuCache.save_submenu_ids(menu_id, submenu_ids)
        SubmenuCache.update_submenu_count(menu_id, 1)
        return model

    @classmethod
    def get_submenu(cls, submenu_id: str) -> SubmenuModel | None:
        submenu_raw = redisCache.get(submenu_id)
        if submenu_raw is None:
            return None
        return SubmenuModel.model_validate_json(submenu_raw)

    @classmethod
    def update_submenu(cls, submenu: Submenu) -> SubmenuModel:
        model: SubmenuModel = SubmenuModel.model_validate(submenu, from_attributes=True)
        redisCache.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        return model

    @classmethod
    def delete_submenu(cls, menu_id: str, submenu_id: str):
        dishes_count = 0
        dish_ids = DishCache.get_dish_ids(submenu_id)
        if dish_ids is not None:
            dishes_count = len(dish_ids)
        submenu_ids = SubmenuCache.get_submenu_ids(menu_id)
        submenu_ids.discard(submenu_id)
        SubmenuCache.save_submenu_ids(menu_id, submenu_ids)
        SubmenuCache.update_submenu_count(menu_id, -1, dishes_count)
        pipe = redisCache.pipeline()
        pipe.delete(submenu_id)
        DishCache.delete_all_dishes(submenu_id, pipe)
        pipe.delete(cls.SUBMENUS_KEY_FORMAT.format(menu_id))
        pipe.execute()

    @classmethod
    def delete_all_submenus(cls, menu_id: str, pipe: Pipeline):
        submenu_ids = cls.get_submenu_ids(menu_id)
        for submenu_id in submenu_ids:
            DishCache.delete_all_dishes(submenu_id, pipe)
            pipe.delete(cls.SUBMENUS_KEY_FORMAT.format(menu_id))
        pipe.delete(*submenu_ids)

    @classmethod
    def get_submenu_ids(cls, menu_id: str) -> set[str]:
        dish_ids_raw = redisCache.get(cls.SUBMENUS_KEY_FORMAT.format(menu_id))
        if dish_ids_raw is None:
            return set()
        dish_ids = set(json.loads(dish_ids_raw.replace("'", '"')))
        return dish_ids

    @classmethod
    def save_submenu_ids(cls, menu_id: str, submenu_ids: set[str]):
        redisCache.set(cls.SUBMENUS_KEY_FORMAT.format(menu_id), json.dumps(
            list(submenu_ids)), ex=cache_settings.CACHE_EXPIRE_SECONDS)

    @classmethod
    def update_submenu_count(cls, menu_id: str, submenus_additional_count: int, deleted_dishes_count: int = 0):
        menu_raw = redisCache.get(menu_id)
        if menu_raw is None:
            return
        menu: MenuModel = MenuModel.model_validate_json(menu_raw)
        menu.submenus_count += submenus_additional_count
        if deleted_dishes_count != 0:
            menu.dishes_count -= deleted_dishes_count
        redisCache.set(menu_id, menu.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)


class DishCache:
    DISHES_KEY_FORMAT = '{0}_dishes'

    def __init__(self):
        pass

    @classmethod
    def add_dishes(cls, submenu_id: str, dishes: list[type[Dish]]) -> list[DishModel]:
        pipe = redisCache.pipeline()
        # смысла забирать из кэша существующие блюда нет - все равно у всех блюд нужно обновить время жизни
        dish_ids = []
        result = []
        for dish in dishes:
            model: DishModel = DishModel.model_validate(dish)
            result.append(model)
            dish_ids.append(model.id)
            pipe.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        pipe.set(cls.DISHES_KEY_FORMAT.format(submenu_id), json.dumps(
            dish_ids), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        pipe.execute()
        return result

    @classmethod
    def get_dishes_of_submenu(cls, submenu_id: str) -> list[DishModel]:
        dish_ids = DishCache.get_dish_ids(submenu_id)
        if not dish_ids:
            return []
        dishes_raw = redisCache.mget(dish_ids)
        if dishes_raw is None or dishes_raw == []:
            return []
        result = []
        for dish_raw in dishes_raw:
            dish: DishModel = DishModel.model_validate_json(dish_raw)
            result.append(dish)
        return result

    @classmethod
    def add_dish(cls, menu_id: str, submenu_id: str, dish: Dish) -> DishModel:
        model: DishModel = DishModel.model_validate(dish, from_attributes=True)
        redisCache.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        dish_ids = DishCache.get_dish_ids(submenu_id)
        dish_ids.add(dish.id)
        cls.save_dish_ids(submenu_id, dish_ids)
        cls.update_dishes_count(menu_id, submenu_id, 1)
        return model

    @classmethod
    def get_dish(cls, dish_id: str) -> DishModel | None:
        dish_raw = redisCache.get(dish_id)
        if dish_raw is None or dish_raw == '':
            return None
        return DishModel.model_validate_json(dish_raw)

    @classmethod
    def update_dish(cls, dish: Dish) -> DishModel:
        model: DishModel = DishModel.model_validate(dish, from_attributes=True)
        redisCache.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        return model

    @classmethod
    def delete_dish(cls, menu_id: str, submenu_id: str, dish_id: str):
        redisCache.delete(dish_id)
        dish_ids = DishCache.get_dish_ids(submenu_id)
        dish_ids.discard(dish_id)
        cls.save_dish_ids(submenu_id, dish_ids)
        cls.update_dishes_count(menu_id, submenu_id, -1)

    @classmethod
    def get_dish_ids(cls, submenu_id: str) -> set[str]:
        dish_ids_raw = redisCache.get(cls.DISHES_KEY_FORMAT.format(submenu_id))
        if dish_ids_raw is None:
            return set()
        dish_ids = set(json.loads(dish_ids_raw.replace("'", '"')))
        return dish_ids

    @classmethod
    def save_dish_ids(cls, submenu_id: str, dish_ids: set[str]):
        redisCache.set(cls.DISHES_KEY_FORMAT.format(submenu_id), json.dumps(
            list(dish_ids)), ex=cache_settings.CACHE_EXPIRE_SECONDS)

    @classmethod
    def update_dishes_count(cls, menu_id, submenu_id: str, additional_dishes_count: int) -> None:
        submenu_raw = redisCache.get(submenu_id)
        if submenu_raw is None:
            return
        submenu: SubmenuModel = SubmenuModel.model_validate_json(submenu_raw)
        submenu.dishes_count += additional_dishes_count
        redisCache.set(submenu_id, submenu.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        menu_raw = redisCache.get(menu_id)
        if menu_raw is None:
            return
        menu: MenuModel = MenuModel.model_validate_json(menu_raw)
        menu.dishes_count += additional_dishes_count
        redisCache.set(menu_id, menu.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)

    @classmethod
    def delete_all_dishes(cls, submenu_id: str, pipe: Pipeline):
        dish_ids = cls.get_dish_ids(submenu_id)
        pipe.delete(*dish_ids)
        pipe.delete(cls.DISHES_KEY_FORMAT.format(submenu_id))
