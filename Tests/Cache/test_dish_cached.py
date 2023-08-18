from typing import Callable

import pytest
from async_asgi_testclient import TestClient

from conftest import ADD_TO_CACHE, func_reverse
from src.app import app
from src.Cache.caches import DishCache, MenuCache, SubmenuCache
from src.Entities.dish import DishModel
from src.Entities.submenu import Submenu

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_all_dish_empty(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload: list = []
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    response = await client.get(func_reverse('get_list_dishes', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id))
    assert response.status_code == 200
    test_all_dishes = await DishCache.get_dishes_of_submenu(test_submenu.id)
    assert test_all_dishes == test_response_payload
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 0
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 0


@pytest.mark.asyncio
async def test_post_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    response = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                              submenu_id=test_submenu.id), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    test_dish_cache = await DishCache.get_dish(test_response_payload['id'])
    test_dish: DishModel = DishModel.model_validate(test_response_payload, from_attributes=True)  # type: ignore
    assert test_dish_cache == test_dish
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 1
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 1


@pytest.mark.asyncio
async def test_get_all_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = [{'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}]
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                   submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.get(func_reverse('get_list_dishes', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id))
    assert response.status_code == 200
    test_response_payload[0]['id'] = response.json()[0]['id']
    test_all_dishes = await DishCache.get_dishes_of_submenu(test_submenu.id)
    test_response_payload[0]: DishModel = DishModel.model_validate(  # type: ignore
        test_response_payload[0], from_attributes=True)  # type: ignore
    assert test_all_dishes == test_response_payload
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 1
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 1


@pytest.mark.asyncio
async def test_get_target_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_response_payload = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                                           submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.get(func_reverse('get_target_dish', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id, dish_id=test_response_payload.json()['id']))
    assert response.status_code == 200
    test_response_payload.id = response.json()['id']
    test_dish_cache = await DishCache.get_dish(test_response_payload.id)
    test_dish: DishModel = DishModel.model_validate(test_response_payload.json(), from_attributes=True)  # type: ignore
    assert test_dish_cache == test_dish
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 1
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 1


@pytest.mark.asyncio
async def test_get_target_dish_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    response = await client.get(func_reverse('get_target_dish', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id,
                                             dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_dish_cache = await DishCache.get_dish('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_dish_cache is None
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 0
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 0


@pytest.mark.asyncio
async def test_patch_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My updated dish 1', 'description': 'My updated dish description 1',
                            'price': '14.50'}
    test_response_payload = {'id': '', 'title': 'My updated dish 1', 'description': 'My updated dish description 1',
                             'price': '14.50'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_post_dish = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                                    submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.patch(func_reverse('patch_dish', menu_id=test_menu.id,
                                               submenu_id=test_submenu.id, dish_id=test_post_dish.json()['id']),
                                  json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    test_dish_cache = await DishCache.get_dish(test_response_payload['id'])
    test_dish: DishModel = DishModel.model_validate(test_response_payload, from_attributes=True)  # type: ignore
    assert test_dish_cache == test_dish
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 1
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 1


@pytest.mark.asyncio
async def test_patch_dish_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    response = await client.get(func_reverse('patch_dish', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id,
                                             dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_dish_cache = await DishCache.get_dish('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_dish_cache is None
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 0
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 0


@pytest.mark.asyncio
async def test_delete_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_dish = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                               submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.delete(func_reverse('delete_dish', menu_id=test_menu.id,
                                                submenu_id=test_submenu.id, dish_id=test_dish.json()['id']))
    assert response.status_code == 200
    test_dish_cache = await DishCache.get_dish(test_dish.json()['id'])
    assert test_dish_cache is None
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 0
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 0


@pytest.mark.asyncio
async def test_delete_dish_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu, test_submenu = await insert_inst(Submenu, storage=ADD_TO_CACHE)
    response = await client.delete(func_reverse('delete_dish', menu_id=test_menu.id,
                                                submenu_id=test_submenu.id,
                                                dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_dish_cache = await DishCache.get_dish('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_dish_cache is None
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1
    assert test_menu.dishes_count == 0
    test_submenu = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu.dishes_count == 0
