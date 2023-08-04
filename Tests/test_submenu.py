from starlette.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_all_submenu_empty(clear_db, insert_menu):
    test_response_payload = []
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_post_submenu(clear_db, insert_menu):
    test_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = {'id': '', 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    response = client.post(f'/api/v1/menus/{test_menu["id"]}/submenus', json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_get_all_submenu(clear_db, insert_menu, insert_submenu):
    test_response_payload = [{'id': '', 'title': 'My submenu 1',
                              'description': 'My submenu description 1', 'dishes_count': 0}]
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_response_payload[0]['id'] = insert_submenu(test_response_payload[0]['title'],
                                                    test_response_payload[0]['description'],
                                                    test_menu['id']).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_submenu(clear_db, insert_menu, insert_submenu):
    test_response_payload = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1',
                             'dishes_count': 0}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_response_payload['id'] = insert_submenu(test_response_payload['title'],
                                                 test_response_payload['description'],
                                                 test_menu['id']).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_response_payload["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_submenu_not_found(clear_db, insert_menu):
    test_response_payload = {'detail': 'submenu not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_patch_submenu(clear_db, insert_menu, insert_submenu):
    test_response_payload = {'id': '', 'title': 'My updated submenu 1',
                             'description': 'My updated submenu description 1', 'dishes_count': 0}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_response_payload['id'] = insert_submenu(test_response_payload['title'],
                                                 test_response_payload['description'], test_menu['id']).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_response_payload["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_patch_submenu_not_found(clear_db, insert_menu):
    test_response_payload = {'detail': 'submenu not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_delete_submenu(clear_db, insert_menu, insert_submenu):
    test_response_payload = {'status': True, 'message': 'The submenu has been deleted'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {'id': '', 'title': 'My updated submenu 1', 'description': 'My updated submenu description 1',
                    'dishes_count': 0}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu['id']).id
    response = client.delete(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_delete_submenu_not_found(clear_db, insert_menu):
    test_response_payload = {'status': False, 'message': 'submenu not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'dishes_count': 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description'])
    response = client.delete(f'/api/v1/menus/{test_menu["id"]}/submenus/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload
