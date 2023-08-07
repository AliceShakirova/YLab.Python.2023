from starlette.testclient import TestClient

from conftest import func_reverse
from src.app import app

client = TestClient(app)


def test_get_all_menu(clear_storage, insert_menu, insert_menu_cache):
    test_response_payload = [{'id': '', 'title': 'My menu 1',
                              'description': 'My menu description 1', 'submenus_count': 0, 'dishes_count': 0}]
    test_response_payload[0]['id'] = insert_menu(title=test_response_payload[0]['title'],
                                                 description=test_response_payload[0]['description']).id
    insert_menu_cache(menu_id=test_response_payload[0]['id'], title=test_response_payload[0]['title'],
                      description=test_response_payload[0]['description'],
                      submenus_count=test_response_payload[0]['submenus_count'],
                      dishes_count=test_response_payload[0]['dishes_count'])
    response = client.get(url=func_reverse('get_list_menus'))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_menu(clear_storage, insert_menu, insert_menu_cache):
    test_response_payload = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_response_payload['id'] = insert_menu(test_response_payload['title'],
                                              test_response_payload['description']).id
    insert_menu_cache(menu_id=test_response_payload['id'], title=test_response_payload['title'],
                      description=test_response_payload['description'],
                      submenus_count=test_response_payload['submenus_count'],
                      dishes_count=test_response_payload['dishes_count'])
    response = client.get(url=func_reverse('get_target_menu', menu_id=test_response_payload['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_patch_menu(clear_storage, insert_menu, insert_menu_cache):
    test_response_payload = {'id': '', 'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_response_payload['id'] = insert_menu(test_response_payload['title'],
                                              test_response_payload['description']).id
    insert_menu_cache(menu_id=test_response_payload['id'], title=test_response_payload['title'],
                      description=test_response_payload['description'],
                      submenus_count=test_response_payload['submenus_count'],
                      dishes_count=test_response_payload['dishes_count'])
    response = client.get(url=func_reverse('patch_menu', menu_id=test_response_payload['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_delete_menu(clear_storage, insert_menu, insert_menu_cache):
    test_response_payload = {'status': True, 'message': 'The menu has been deleted'}
    test_menu = {'id': '', 'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                 'submenus_count': 0, 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'],
                      description=test_menu['description'], submenus_count=test_menu['submenus_count'],
                      dishes_count=test_menu['dishes_count'])
    response = client.delete(url=func_reverse('delete_menu', menu_id=test_menu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload
