from starlette.testclient import TestClient

import conftest
from conftest import func_reverse
from src.app import app
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu

client = TestClient(app)


def test_get_all_submenu_empty(clear_storage, insert_inst):
    test_response_payload = []
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.get(url=func_reverse('get_list_submenus', menu_id=test_menu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_post_submenu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = {'id': '', 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.post(url=func_reverse('post_submenu', menu_id=test_menu['id']), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_get_all_submenu(clear_storage, insert_inst):
    test_response_payload = [{'id': '', 'title': 'My submenu 1',
                              'description': 'My submenu description 1', 'dishes_count': 0}]
    test_menu, test_response_payload[0] = insert_inst(Submenu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.get(url=func_reverse('get_list_submenus', menu_id=test_menu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_submenu(clear_storage, insert_inst):
    test_menu, test_response_payload = insert_inst(Submenu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.get(url=func_reverse('get_target_submenu', menu_id=test_menu['id'],
                                           submenu_id=test_response_payload['id']))
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_get_target_submenu_not_found(clear_storage, insert_inst):
    test_response_payload = {'detail': 'submenu not found'}
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.get(url=func_reverse('get_target_submenu', menu_id=test_menu['id'],
                                           submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_patch_submenu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My updated submenu 1', 'description': 'My updated submenu description 1',
                            'dishes_count': 0}
    test_response_payload = {'id': '', 'title': 'My updated submenu 1',
                             'description': 'My updated submenu description 1', 'dishes_count': 0}
    test_menu, test_submenu = insert_inst(Submenu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.patch(url=func_reverse('patch_submenu', menu_id=test_menu['id'],
                                             submenu_id=test_submenu['id']), json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_patch_submenu_not_found(clear_storage, insert_inst):
    test_response_payload = {'detail': 'submenu not found'}
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.get(url=func_reverse('patch_submenu', menu_id=test_menu['id'],
                                           submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_delete_submenu(clear_storage, insert_inst):
    test_response_payload = {'status': True, 'message': 'The submenu has been deleted'}
    test_menu, test_submenu = insert_inst(Submenu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.delete(url=func_reverse('delete_submenu', menu_id=test_menu['id'],
                                              submenu_id=test_submenu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_delete_submenu_not_found(clear_storage, insert_inst):
    test_response_payload = {'status': False, 'message': 'submenu not found'}
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.delete(url=func_reverse('delete_submenu', menu_id=test_menu['id'],
                                              submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload
