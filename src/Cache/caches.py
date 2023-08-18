import json
from contextlib import asynccontextmanager
from os import getenv
from typing import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio.client import Pipeline

from src.Cache import cache_settings
from src.Entities.dish import Dish, DishModel
from src.Entities.menu import Menu, MenuModel
from src.Entities.submenu import Submenu, SubmenuModel

conn_str_env = getenv('REDIS_OM_URL')
if conn_str_env is None:
    conn_str = 'redis://@localhost:6379'
else:
    conn_str = conn_str_env


async def init_cache() -> None:
    redis_cache = redis.from_url(conn_str, decode_responses=True)
    await redis_cache.close(close_connection_pool=False)


@asynccontextmanager
async def get_redis() -> AsyncGenerator:
    redis_conn: redis.Redis
    async with redis.from_url(conn_str, decode_responses=True) as redis_conn:
        try:
            yield redis_conn
        finally:
            await redis_conn.close(close_connection_pool=False)


async def clear_cache() -> None:
    redis_cache: redis.Redis
    async with get_redis() as redis_cache:
        await redis_cache.flushdb()


class MenuCache:
    all_menus_key = 'all_menus'

    @classmethod
    async def get_all_menus(cls) -> list[MenuModel]:
        async with get_redis() as redis:
            all_menu_ids = await cls.get_all_menu_ids()
            if len(all_menu_ids) == 0:
                return []
            all_menus_json = await redis.mget(all_menu_ids)

        result = []
        for menu_json in all_menus_json:
            model: MenuModel = MenuModel.model_validate_json(menu_json)
            result.append(model)
        return result

    @classmethod
    async def add_menu(cls, menu: Menu) -> MenuModel:
        model: MenuModel = MenuModel.model_validate(menu, from_attributes=True)
        async with get_redis() as redis:
            await redis.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
            menu_ids = await MenuCache.get_all_menu_ids()
            menu_ids.add(model.id)
            await MenuCache.save_all_menu_ids(menu_ids)
        return model

    @classmethod
    async def get_menu(cls, menu_id: str) -> MenuModel | None:
        async with get_redis() as redis:
            menu_json = await redis.get(menu_id)
        if menu_json is None:
            return None
        return MenuModel.model_validate_json(menu_json)

    @classmethod
    async def update_menu(cls, menu: Menu) -> MenuModel:
        model: MenuModel = MenuModel.model_validate(menu, from_attributes=True)
        async with get_redis() as redis:
            await redis.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        return model

    @classmethod
    async def delete_menu(cls, menu_id: str) -> None:
        async with get_redis() as redis:
            pipe = redis.pipeline()
            pipe.delete(menu_id)
            menu_ids = await MenuCache.get_all_menu_ids()
            menu_ids.discard(menu_id)
            await MenuCache.save_all_menu_ids(menu_ids, pipe)
            await SubmenuCache.delete_all_submenus(menu_id, pipe)
            await pipe.execute()

    @classmethod
    async def get_all_menu_ids(cls, ) -> set[str]:
        async with get_redis() as redis:
            menu_ids_json = await redis.get(cls.all_menus_key)
        if menu_ids_json is None:
            return set()
        menu_ids = set(json.loads(menu_ids_json.replace("'", '"')))
        return menu_ids

    @classmethod
    async def save_all_menu_ids(cls, menu_ids: set[str], pipe: Pipeline | None = None) -> None:
        if pipe:
            pipe.set(cls.all_menus_key, json.dumps(list(menu_ids)), ex=cache_settings.CACHE_EXPIRE_SECONDS)
            return
        async with get_redis() as redis:
            await redis.set(cls.all_menus_key, json.dumps(list(menu_ids)), ex=cache_settings.CACHE_EXPIRE_SECONDS)


class SubmenuCache:
    SUBMENUS_KEY_FORMAT = '{menu_id}_submenus'

    @classmethod
    async def get_submenus(cls, menu_id: str) -> list[SubmenuModel]:
        submenu_ids = await SubmenuCache.get_submenu_ids(menu_id)
        if not submenu_ids:
            return []

        async with get_redis() as redis:
            submenus_json = await redis.mget(submenu_ids)
        if submenus_json is None or submenus_json == []:
            return []

        result = []
        for submenu_json in submenus_json:
            submenu: SubmenuModel = SubmenuModel.model_validate_json(submenu_json)
            result.append(submenu)
        return result

    @classmethod
    async def add_submenu(cls, submenu: Submenu) -> SubmenuModel:
        model: SubmenuModel = SubmenuModel.model_validate(submenu, from_attributes=True)
        async with get_redis() as redis:
            await redis.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        submenu_ids = await SubmenuCache.get_submenu_ids(submenu.menu_id)
        submenu_ids.add(model.id)
        await SubmenuCache.save_submenu_ids(submenu.menu_id, submenu_ids)
        await SubmenuCache.update_submenu_count(submenu.menu_id, 1)
        return model

    @classmethod
    async def get_submenu(cls, submenu_id: str) -> SubmenuModel | None:
        async with get_redis() as redis:
            submenu_json = await redis.get(submenu_id)
        if submenu_json is None:
            return None
        return SubmenuModel.model_validate_json(submenu_json)

    @classmethod
    async def update_submenu(cls, submenu: Submenu) -> SubmenuModel:
        model: SubmenuModel = SubmenuModel.model_validate(submenu, from_attributes=True)
        async with get_redis() as redis:
            await redis.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        return model

    @classmethod
    async def delete_submenu(cls, menu_id: str, submenu_id: str) -> None:
        dishes_count = 0
        dish_ids = await DishCache.get_dish_ids(submenu_id)
        if dish_ids is not None:
            dishes_count = len(dish_ids)
        submenu_ids = await SubmenuCache.get_submenu_ids(menu_id)
        submenu_ids.discard(submenu_id)
        await SubmenuCache.save_submenu_ids(menu_id, submenu_ids)
        await SubmenuCache.update_submenu_count(menu_id, -1, dishes_count)
        async with get_redis() as redis:
            pipe = redis.pipeline()
            pipe.delete(submenu_id)
            pipe.delete(cls.SUBMENUS_KEY_FORMAT.format(menu_id=menu_id))
            await pipe.execute()
        await DishCache.delete_all_dishes(submenu_id, pipe)

    @classmethod
    async def delete_all_submenus(cls, menu_id: str, pipe: Pipeline) -> None:
        submenu_ids = await cls.get_submenu_ids(menu_id)
        for submenu_id in submenu_ids:
            await DishCache.delete_all_dishes(submenu_id, pipe)
            pipe.delete(cls.SUBMENUS_KEY_FORMAT.format(menu_id=menu_id))
            pipe.delete(submenu_id)

    @classmethod
    async def get_submenu_ids(cls, menu_id: str) -> set[str]:
        async with get_redis() as redis:
            submenu_ids_json = await redis.get(cls.SUBMENUS_KEY_FORMAT.format(menu_id=menu_id))
        if submenu_ids_json is None:
            return set()
        submenu_ids = set(json.loads(submenu_ids_json.replace("'", '"')))
        return submenu_ids

    @classmethod
    async def save_submenu_ids(cls, menu_id: str, submenu_ids: set[str]) -> None:
        async with get_redis() as redis:
            await redis.set(cls.SUBMENUS_KEY_FORMAT.format(menu_id=menu_id),
                            json.dumps(list(submenu_ids)), ex=cache_settings.CACHE_EXPIRE_SECONDS)

    @classmethod
    async def update_submenu_count(cls, menu_id: str, submenus_additional_count: int,
                                   deleted_dishes_count: int = 0) -> None:
        async with get_redis() as redis:
            menu_json = await redis.get(menu_id)
            if menu_json is None:
                return
            menu: MenuModel = MenuModel.model_validate_json(menu_json)
            menu.submenus_count += submenus_additional_count
            if deleted_dishes_count != 0:
                menu.dishes_count -= deleted_dishes_count
            await redis.set(menu_id, menu.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)


class DishCache:
    DISHES_KEY_FORMAT = '{submenu_id}_dishes'

    @classmethod
    async def add_dishes(cls, submenu_id: str, dishes: list[type[Dish]]) -> list[DishModel]:
        async with get_redis() as redis:
            pipe = redis.pipeline()
            # смысла забирать из кэша существующие блюда нет - все равно у всех блюд нужно обновить время жизни
            dish_ids = []
            result = []
            for dish in dishes:
                model: DishModel = DishModel.model_validate(dish)
                result.append(model)
                dish_ids.append(model.id)
                pipe.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
            pipe.set(cls.DISHES_KEY_FORMAT.format(submenu_id=submenu_id), json.dumps(
                dish_ids), ex=cache_settings.CACHE_EXPIRE_SECONDS)
            await pipe.execute()
        return result

    @classmethod
    async def get_dishes_of_submenu(cls, submenu_id: str) -> list[DishModel]:
        dish_ids = await DishCache.get_dish_ids(submenu_id)
        if not dish_ids:
            return []
        async with get_redis() as redis:
            dishes_json = await redis.mget(dish_ids)
        if dishes_json is None or dishes_json == []:
            return []
        result = []
        for dish_json in dishes_json:
            dish: DishModel = DishModel.model_validate_json(dish_json)
            result.append(dish)
        return result

    @classmethod
    async def add_dish(cls, menu_id: str, dish: Dish) -> DishModel:
        model: DishModel = DishModel.model_validate(dish, from_attributes=True)
        async with get_redis() as redis:
            await redis.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
        dish_ids = await DishCache.get_dish_ids(dish.submenu_id)
        dish_ids.add(dish.id)
        await cls.save_dish_ids(dish.submenu_id, dish_ids)
        await cls.update_dishes_count(menu_id, dish.submenu_id, 1)
        return model

    @classmethod
    async def get_dish(cls, dish_id: str) -> DishModel | None:
        async with get_redis() as redis:
            dish_json = await redis.get(dish_id)
        if dish_json is None or dish_json == '':
            return None
        return DishModel.model_validate_json(dish_json)

    @classmethod
    async def update_dish(cls, dish: Dish) -> None:
        model: DishModel = DishModel.model_validate(dish, from_attributes=True)
        async with get_redis() as redis:
            await redis.set(model.id, model.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)

    @classmethod
    async def delete_dish(cls, menu_id: str, submenu_id: str, dish_id: str) -> None:
        async with get_redis() as redis:
            if await redis.get(dish_id) is not None:
                await redis.delete(dish_id)
                await cls.update_dishes_count(menu_id, submenu_id, -1)
        dish_ids = await DishCache.get_dish_ids(submenu_id)
        dish_ids.discard(dish_id)
        await cls.save_dish_ids(submenu_id, dish_ids)

    @classmethod
    async def get_dish_ids(cls, submenu_id: str) -> set[str]:
        async with get_redis() as redis:
            dish_ids_json = await redis.get(cls.DISHES_KEY_FORMAT.format(submenu_id=submenu_id))
        if dish_ids_json is None:
            return set()
        dish_ids = set(json.loads(dish_ids_json.replace("'", '"')))
        return dish_ids

    @classmethod
    async def save_dish_ids(cls, submenu_id: str, dish_ids: set[str]) -> None:
        async with get_redis() as redis:
            await redis.set(cls.DISHES_KEY_FORMAT.format(submenu_id=submenu_id),
                            json.dumps(list(dish_ids)), ex=cache_settings.CACHE_EXPIRE_SECONDS)

    @classmethod
    async def update_dishes_count(cls, menu_id, submenu_id: str, additional_dishes_count: int) -> None:
        async with get_redis() as redis:
            submenu_json = await redis.get(submenu_id)
            if submenu_json is None:
                return
            submenu: SubmenuModel = SubmenuModel.model_validate_json(submenu_json)
            submenu.dishes_count += additional_dishes_count
            await redis.set(submenu_id, submenu.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)
            menu_json = await redis.get(menu_id)
            if menu_json is None:
                return
            menu: MenuModel = MenuModel.model_validate_json(menu_json)
            menu.dishes_count += additional_dishes_count
            await redis.set(menu_id, menu.model_dump_json(), ex=cache_settings.CACHE_EXPIRE_SECONDS)

    @classmethod
    async def delete_all_dishes(cls, submenu_id: str, pipe: Pipeline) -> None:
        dish_ids = await cls.get_dish_ids(submenu_id)
        for dish_id in dish_ids:
            pipe.delete(dish_id)
        pipe.delete(cls.DISHES_KEY_FORMAT.format(submenu_id=submenu_id))
