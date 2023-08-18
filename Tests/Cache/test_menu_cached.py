from typing import Callable

import pytest
from async_asgi_testclient import TestClient

import conftest
from conftest import func_reverse
from src.app import app
from src.Cache.caches import MenuCache

# from src.Entities.dish import Dish
from src.Entities.menu import Menu, MenuModel

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_all_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = [{'id': '', 'title': 'My menu 1',
                              'description': 'My menu description 1', 'submenus_count': 0, 'dishes_count': 0}]
    test_response_payload[0]['id'] = (await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)).id
    response = await client.get(func_reverse('get_list_menus'))
    assert response.status_code == 200
    test_all_menus = await MenuCache.get_all_menus()
    test_response_payload[0]: MenuModel = MenuModel.model_validate(  # type: ignore
        test_response_payload[0], from_attributes=True)  # type: ignore
    assert test_all_menus[0] == test_response_payload[0]


@pytest.mark.asyncio
async def test_get_target_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    response = await client.get(func_reverse('get_target_menu', menu_id=test_response_payload.id))
    assert response.status_code == 200
    test_response_payload.id = response.json()['id']
    test_menu_cache = await MenuCache.get_menu(test_response_payload.id)
    test_response_payload: MenuModel = MenuModel.model_validate(  # type: ignore
        test_response_payload, from_attributes=True)  # type: ignore
    assert test_menu_cache == test_response_payload


@pytest.mark.asyncio
async def test_patch_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                            'submenus_count': 0, 'dishes_count': 0}
    test_response_payload = {'id': '', 'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    response = await client.patch(func_reverse('patch_menu', menu_id=test_menu.id), json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    test_menu_cache = await MenuCache.get_menu(test_menu.id)
    test_menu: MenuModel = MenuModel.model_validate(test_response_payload, from_attributes=True)  # type: ignore
    assert test_menu_cache == test_menu


@pytest.mark.asyncio
async def test_delete_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    response = await client.delete(func_reverse('delete_menu', menu_id=test_menu.id))
    assert response.status_code == 200
    test_menu_cache = await MenuCache.get_menu(test_menu.id)
    assert test_menu_cache is None
