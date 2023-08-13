import pytest
from async_asgi_testclient import TestClient

from conftest import func_reverse
from src.app import app

client = TestClient(app)
menu_id = None
submenu_id = None
dish1_id = None
dish2_id = None


@pytest.mark.asyncio
@pytest.mark.order(1)
async def test_post_menu(start_clear_storage):
    test_request_payload = {'title': 'My menu 1', 'description': 'My menu description 1'}
    test_response_payload = {'title': 'My menu 1',
                             'description': 'My menu description 1', 'submenus_count': 0, 'dishes_count': 0}

    response = await client.post(func_reverse('post_menu'), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    global menu_id
    menu_id = test_response_payload['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(2)
async def test_post_submenu():
    test_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = {'id': menu_id, 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}
    response = await client.post(func_reverse('post_submenu', menu_id=menu_id), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    global submenu_id
    submenu_id = test_response_payload['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(3)
async def test_post_dish_1():
    test_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    response = await client.post(func_reverse('post_dish', menu_id=menu_id, submenu_id=submenu_id),
                                 json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    global dish1_id
    dish1_id = test_response_payload['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(4)
async def test_post_dish_2():
    test_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    response = await client.post(func_reverse('post_dish', menu_id=menu_id, submenu_id=submenu_id),
                                 json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    global dish2_id
    dish2_id = test_response_payload['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(5)
async def test_get_target_menu_1():
    test_response_payload = {'id': menu_id, 'title': 'My menu 1', 'description': 'My menu description 1',
                             'submenus_count': 1, 'dishes_count': 2}
    response = await client.get(func_reverse('get_target_menu', menu_id=menu_id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(6)
async def test_get_target_submenu():
    test_response_payload = {'id': submenu_id, 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 2}
    response = await client.get(func_reverse('get_target_submenu', menu_id=menu_id, submenu_id=submenu_id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(7)
async def test_delete_submenu():
    test_response_payload = {'status': True, 'message': 'The submenu has been deleted'}
    response = await client.delete(func_reverse('delete_submenu', menu_id=menu_id, submenu_id=submenu_id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(8)
async def test_get_all_submenu_empty():
    test_response_payload = []
    response = await client.get(func_reverse('get_list_submenus', menu_id=menu_id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(9)
async def test_get_all_dish_empty():
    test_response_payload = []
    response = await client.get(func_reverse('get_list_dishes', menu_id=menu_id, submenu_id=submenu_id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(10)
async def test_get_target_menu_2():
    test_response_payload = {'id': menu_id, 'title': 'My menu 1', 'description': 'My menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    response = await client.get(func_reverse('get_target_menu', menu_id=menu_id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(11)
async def test_delete_menu():
    test_response_payload = {'status': True, 'message': 'The menu has been deleted'}
    response = await client.delete(func_reverse('delete_menu', menu_id=menu_id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
@pytest.mark.order(12)
async def test_get_all_menu_empty():
    test_response_payload = []
    response = await client.get(func_reverse('get_list_menus'))
    assert response.status_code == 200
    assert response.json() == test_response_payload
