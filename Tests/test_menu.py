import pytest
from async_asgi_testclient import TestClient

import conftest
from conftest import func_reverse
from src.app import app
from src.Entities.menu import Menu, MenuModel

# from src.Entities.submenu import Submenu

client = TestClient(app)


"""
@pytest.mark.asyncio
async def test_get_all_inst(clear_storage, insert_inst):
    test_response_payload = [{'id': '', 'title': 'My menu 1', 'description': 'My menu description 1',
                              'submenus_count': 1, 'dishes_count': 1},
                             {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1',
                              'dishes_count': 1},
                             {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}]
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_CACHE)
    test_dish_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_dish = await client.post(func_reverse('post_dish', menu_id=test_menu.id,
                                             submenu_id=test_submenu.id), json=test_dish_request_payload)
    response = await client.get(func_reverse('get_all_menus_submenus_and_dishes'))
    assert response.status_code == 200
    test_response_payload[0]['id'] = test_menu.id
    test_response_payload[1]['id'] = test_submenu.id
    test_response_payload[2]['id'] = test_dish.json()['id']
    assert response.json() == test_response_payload"""

"""
@pytest.mark.asyncio
async def test_get_all_menu_empty_storage(clear_storage):
    test_response_payload = []
    response = await client.get(func_reverse('get_list_menus'))
    assert response.status_code == 200
    assert response.json() == test_response_payload"""


@pytest.mark.asyncio
async def test_post_menu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My menu 1', 'description': 'My menu description 1'}
    test_response_payload = await insert_inst(Menu, storage=conftest.NOT_ADD)
    response = await client.post(func_reverse('post_menu'), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload.id = response.json()['id']
    model: MenuModel = MenuModel.model_validate(response.json(), from_attributes=True)  # type: ignore
    assert model == test_response_payload


@pytest.mark.asyncio
async def test_get_all_menu(clear_storage, insert_inst):
    test_response_payload = [{'id': '', 'title': 'My menu 1',
                              'description': 'My menu description 1', 'submenus_count': 0, 'dishes_count': 0}]
    test_response_payload[0]['id'] = (await insert_inst(Menu, storage=conftest.ADD_TO_DB)).id
    response = await client.get(func_reverse('get_list_menus'))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_get_target_menu(clear_storage, insert_inst):
    test_response_payload = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('get_target_menu', menu_id=test_menu.id))
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id'] = test_menu.id
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_get_target_menu_not_found(clear_storage):
    test_response_payload = {'detail': 'menu not found'}
    response = await client.get(func_reverse('get_target_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_patch_menu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                            'submenus_count': 0, 'dishes_count': 0}
    test_response_payload = {'id': '', 'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.patch(func_reverse('patch_menu', menu_id=test_menu.id), json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_patch_menu_not_found(clear_storage):
    test_response_payload = {'detail': 'menu not found'}
    response = await client.get(func_reverse('patch_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_delete_menu(clear_storage, insert_inst):
    test_response_payload = {'status': True, 'message': 'The menu has been deleted'}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.delete(func_reverse('delete_menu', menu_id=test_menu.id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_delete_menu_not_found(clear_storage):
    test_response_payload = {'status': False, 'message': 'menu not found'}
    response = await client.delete(func_reverse('delete_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload
