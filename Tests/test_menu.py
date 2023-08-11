from starlette.testclient import TestClient

import conftest
from conftest import func_reverse
from src.app import app
from src.Entities.menu import Menu

client = TestClient(app)


def test_get_all_menu_empty_storage(clear_storage):
    clear_storage()
    test_response_payload = []
    response = client.get(url=func_reverse('get_list_menus'))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_post_menu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My menu 1', 'description': 'My menu description 1'}
    test_response_payload = insert_inst(Menu, updated=False, storage=conftest.NOT_ADD)
    response = client.post(url=func_reverse('post_menu'), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_get_all_menu(clear_storage, insert_inst):
    test_response_payload = [{'id': '', 'title': 'My menu 1',
                              'description': 'My menu description 1', 'submenus_count': 0, 'dishes_count': 0}]
    test_response_payload[0]['id'] = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)['id']
    response = client.get(url=func_reverse('get_list_menus'))
    assert response.status_code == 200
    test_response_payload[0]['id'] = response.json()[0]['id']
    assert response.json() == test_response_payload


def test_get_target_menu(clear_storage, insert_inst):
    test_response_payload = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_response_payload['id'] = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)['id']
    response = client.get(url=func_reverse('get_target_menu', menu_id=test_response_payload['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_menu_not_found(clear_storage):
    test_response_payload = {'detail': 'menu not found'}
    response = client.get(url=func_reverse('get_target_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_patch_menu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                            'submenus_count': 0, 'dishes_count': 0}
    test_response_payload = {'id': '', 'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.patch(url=func_reverse('patch_menu', menu_id=test_menu['id']), json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_patch_menu_not_found(clear_storage):
    test_response_payload = {'detail': 'menu not found'}
    response = client.get(url=func_reverse('patch_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_delete_menu(clear_storage, insert_inst):
    test_response_payload = {'status': True, 'message': 'The menu has been deleted'}
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_DB)
    response = client.delete(url=func_reverse('delete_menu', menu_id=test_menu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_delete_menu_not_found(clear_storage):
    test_response_payload = {'status': False, 'message': 'menu not found'}
    response = client.delete(url=func_reverse('delete_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload
