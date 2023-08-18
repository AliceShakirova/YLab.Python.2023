from typing import Callable

import pytest
from async_asgi_testclient import TestClient

import conftest
from conftest import func_reverse
from src.app import app
from src.Cache.caches import MenuCache, SubmenuCache
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu, SubmenuModel

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_all_submenu_empty(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload: list = []
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    response = await client.get(func_reverse('get_list_submenus', menu_id=test_menu.id))
    assert response.status_code == 200
    test_all_submenus = await SubmenuCache.get_submenus(test_menu.id)
    assert test_all_submenus == test_response_payload
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 0


@pytest.mark.asyncio
async def test_post_submenu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload: dict[str, str | int] = {'id': '', 'title': 'My submenu 1',
                                                   'description': 'My submenu description 1', 'dishes_count': 0}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    response = await client.post(func_reverse('post_submenu', menu_id=test_menu.id), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    test_submenu_cache = await SubmenuCache.get_submenu(test_response_payload['id'])  # type: ignore
    test_submenu: SubmenuModel = SubmenuModel.model_validate(  # type: ignore
        test_response_payload, from_attributes=True)  # type: ignore
    assert test_submenu_cache == test_submenu
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1


@pytest.mark.asyncio
async def test_get_all_submenu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_submenu_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = [{'id': '', 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}]
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    await client.post(func_reverse('post_submenu', menu_id=test_menu.id),
                      json=test_submenu_request_payload)
    response = await client.get(func_reverse('get_list_submenus', menu_id=test_menu.id))
    assert response.status_code == 200
    test_response_payload[0]['id'] = response.json()[0]['id']
    test_all_submenus = await SubmenuCache.get_submenus(test_menu.id)
    test_response_payload[0]: SubmenuModel = SubmenuModel.model_validate(  # type: ignore
        test_response_payload[0], from_attributes=True)  # type: ignore
    assert test_all_submenus == test_response_payload
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1


@pytest.mark.asyncio
async def test_get_target_submenu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu, test_response_payload = await insert_inst(Submenu, storage=conftest.ADD_TO_CACHE)
    response = await client.get(func_reverse('get_target_submenu', menu_id=test_menu.id,
                                             submenu_id=test_response_payload.id))
    assert response.status_code == 200
    test_response_payload.id = response.json()['id']
    test_submenu_cache = await SubmenuCache.get_submenu(test_response_payload.id)
    test_submenu: SubmenuModel = SubmenuModel.model_validate(  # type: ignore
        test_response_payload, from_attributes=True)  # type: ignore
    assert test_submenu_cache == test_submenu
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1


@pytest.mark.asyncio
async def test_get_target_submenu_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    response = await client.get(func_reverse('get_target_submenu', menu_id=test_menu.id,
                                             submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_submenu_cache = await SubmenuCache.get_submenu('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_submenu_cache is None
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 0


@pytest.mark.asyncio
async def test_patch_submenu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My updated submenu 1', 'description': 'My updated submenu description 1'}
    test_response_payload = {'id': '', 'title': 'My updated submenu 1',
                             'description': 'My updated submenu description 1', 'dishes_count': 0}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_CACHE)
    response = await client.patch(func_reverse('patch_submenu', menu_id=test_menu.id,
                                               submenu_id=test_submenu.id), json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    test_submenu_cache = await SubmenuCache.get_submenu(test_response_payload['id'])  # type: ignore
    test_submenu: SubmenuModel = SubmenuModel.model_validate(  # type: ignore
        test_response_payload, from_attributes=True)  # type: ignore
    assert test_submenu_cache == test_submenu
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 1


@pytest.mark.asyncio
async def test_patch_submenu_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    response = await client.get(func_reverse('patch_submenu', menu_id=test_menu.id,
                                             submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_submenu_cache = await SubmenuCache.get_submenu('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_submenu_cache is None
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 0


@pytest.mark.asyncio
async def test_delete_submenu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_CACHE)
    response = await client.delete(func_reverse('delete_submenu', menu_id=test_menu.id,
                                                submenu_id=test_submenu.id))
    assert response.status_code == 200
    test_submenu_cache = await SubmenuCache.get_submenu(test_submenu.id)
    assert test_submenu_cache is None
    test_menu = await MenuCache.get_menu(test_menu.id)
    assert test_menu.submenus_count == 0


@pytest.mark.asyncio
async def test_delete_submenu_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_CACHE)
    response = await client.delete(func_reverse('delete_submenu', menu_id=test_menu.id,
                                                submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_submenu_cache = await SubmenuCache.get_submenu('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_submenu_cache is None
