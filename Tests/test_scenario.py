import pytest
from starlette.testclient import TestClient

from src.app import app

client = TestClient(app)
menu_id = None
submenu_id = None
dish1_id = None
dish2_id = None


@pytest.mark.order(1)
def test_post_menu(start_clear_db):
    start_clear_db()
    test_request_payload = {'title': 'My menu 1', 'description': 'My menu description 1'}
    test_response_payload = {'title': 'My menu 1',
                             'description': 'My menu description 1', 'submenus_count': 0, 'dishes_count': 0}

    response = client.post('/api/v1/menus', json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    global menu_id
    menu_id = test_response_payload['id']
    assert response.json() == test_response_payload


@pytest.mark.order(2)
def test_post_submenu():
    test_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = {'id': menu_id, 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}
    response = client.post(f'/api/v1/menus/{menu_id}/submenus', json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    global submenu_id
    submenu_id = test_response_payload['id']
    assert response.json() == test_response_payload


@pytest.mark.order(3)
def test_post_dish_1():
    test_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    response = client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    global dish1_id
    dish1_id = test_response_payload['id']
    assert response.json() == test_response_payload


@pytest.mark.order(4)
def test_post_dish_2():
    test_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    response = client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    global dish2_id
    dish2_id = test_response_payload['id']
    assert response.json() == test_response_payload


@pytest.mark.order(5)
def test_get_target_menu_1():
    test_response_payload = {'id': menu_id, 'title': 'My menu 1', 'description': 'My menu description 1',
                             'submenus_count': 1, 'dishes_count': 2}
    response = client.get(f'/api/v1/menus/{menu_id}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.order(6)
def test_get_target_submenu():
    test_response_payload = {'id': submenu_id, 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 2}
    response = client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.order(7)
def test_delete_submenu():
    test_response_payload = {'status': True, 'message': 'The submenu has been deleted'}
    response = client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.order(8)
def test_get_all_submenu_empty():
    test_response_payload = []
    response = client.get(f'/api/v1/menus/{menu_id}/submenus')
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.order(9)
def test_get_all_dish_empty():
    test_response_payload = []
    response = client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.order(10)
def test_get_target_menu_2():
    test_response_payload = {'id': menu_id, 'title': 'My menu 1', 'description': 'My menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    response = client.get(f'/api/v1/menus/{menu_id}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.order(11)
def test_delete_menu():
    test_response_payload = {'status': True, 'message': 'The menu has been deleted'}
    response = client.delete(f'/api/v1/menus/{menu_id}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.order(12)
def test_get_all_menu_empty():
    test_response_payload = []
    response = client.get('/api/v1/menus')
    assert response.status_code == 200
    assert response.json() == test_response_payload
