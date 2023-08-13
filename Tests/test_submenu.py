import pytest
from async_asgi_testclient import TestClient

import conftest
from conftest import func_reverse
from src.app import app
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu, SubmenuModel

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_all_submenu_empty(clear_storage, insert_inst):
    test_response_payload = []
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('get_list_submenus', menu_id=test_menu.id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_post_submenu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = {'id': '', 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.post(func_reverse('post_submenu', menu_id=test_menu.id), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_get_all_submenu(clear_storage, insert_inst):
    test_response_payload = [{'id': '', 'title': 'My submenu 1',
                              'description': 'My submenu description 1', 'dishes_count': 0}]
    test_menu, test_response_payload[0] = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('get_list_submenus', menu_id=test_menu.id))
    assert response.status_code == 200
    test_response_payload[0].id = response.json()[0]['id']
    model: SubmenuModel = SubmenuModel.model_validate(response.json()[0], from_attributes=True)  # type: ignore
    assert [model] == test_response_payload


@pytest.mark.asyncio
async def test_get_target_submenu(clear_storage, insert_inst):
    test_menu, test_response_payload = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('get_target_submenu', menu_id=test_menu.id,
                                             submenu_id=test_response_payload.id))
    assert response.status_code == 200
    test_response_payload.id = response.json()['id']
    model: SubmenuModel = SubmenuModel.model_validate(response.json(), from_attributes=True)  # type: ignore
    assert model == test_response_payload


@pytest.mark.asyncio
async def test_get_target_submenu_not_found(clear_storage, insert_inst):
    test_response_payload = {'detail': 'submenu not found'}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('get_target_submenu', menu_id=test_menu.id,
                                             submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_patch_submenu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My updated submenu 1', 'description': 'My updated submenu description 1',
                            'dishes_count': 0}
    test_response_payload = {'id': '', 'title': 'My updated submenu 1',
                             'description': 'My updated submenu description 1', 'dishes_count': 0}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.patch(func_reverse('patch_submenu', menu_id=test_menu.id,
                                               submenu_id=test_submenu.id), json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_patch_submenu_not_found(clear_storage, insert_inst):
    test_response_payload = {'detail': 'submenu not found'}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('patch_submenu', menu_id=test_menu.id,
                                             submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_delete_submenu(clear_storage, insert_inst):
    test_response_payload = {'status': True, 'message': 'The submenu has been deleted'}
    test_menu, test_submenu = await insert_inst(Submenu, storage=conftest.ADD_TO_DB)
    response = await client.delete(func_reverse('delete_submenu', menu_id=test_menu.id,
                                                submenu_id=test_submenu.id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_delete_submenu_not_found(clear_storage, insert_inst):
    test_response_payload = {'status': False, 'message': 'submenu not found'}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.delete(func_reverse('delete_submenu', menu_id=test_menu.id,
                                                submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload
