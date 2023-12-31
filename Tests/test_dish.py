from typing import Callable

import pytest
from async_asgi_testclient import TestClient

import conftest
from conftest import func_reverse
from src.app import app
from src.Entities.submenu import Submenu

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_all_dish_empty(clear_storage, insert_inst):
    test_response_payload = []
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('get_list_dishes', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_post_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                              submenu_id=test_submenu.id), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_get_all_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = [{'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}]
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                   submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.get(func_reverse('get_list_dishes', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id))
    assert response.status_code == 200
    test_response_payload[0]['id'] = response.json()[0]['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_get_target_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_dish = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                               submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.get(func_reverse('get_target_dish', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id, dish_id=test_dish.json()['id']))
    assert response.status_code == 200
    test_response_payload['id'] = test_dish.id = response.json()['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_get_target_dish_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = {'detail': 'dish not found'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('get_target_dish', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id,
                                             dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_patch_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My updated dish 1', 'description': 'My updated dish description 1',
                            'price': '14.50'}
    test_response_payload = {'id': '', 'title': 'My updated dish 1', 'description': 'My updated dish description 1',
                             'price': '14.50'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_dish = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                               submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.patch(func_reverse('patch_dish', menu_id=test_menu.id,
                                               submenu_id=test_submenu.id, dish_id=test_dish.json()['id']),
                                  json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_patch_dish_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = {'detail': 'dish not found'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('patch_dish', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id,
                                             dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_delete_dish(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = {'status': True, 'message': 'The dish has been deleted'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_dish = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                               submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.delete(func_reverse('delete_dish', menu_id=test_menu.id,
                                                submenu_id=test_submenu.id, dish_id=test_dish.json()['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_delete_dish_not_found(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = {'status': False, 'message': 'dish not found'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.delete(func_reverse('delete_dish', menu_id=test_menu.id,
                                                submenu_id=test_submenu.id,
                                                dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload
