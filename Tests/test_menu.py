from starlette.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_all_menu_empty(clear_db):
    clear_db()
    test_response_payload = []
    response = client.get('/api/v1/menus')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_post_menu(clear_db):
    test_request_payload = {"title": "My menu 1", "description": "My menu description 1"}
    test_response_payload = {"id": '', "title": "My menu 1",
                             "description": "My menu description 1", "submenus_count": 0, "dishes_count": 0}

    response = client.post('/api/v1/menus', json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_get_all_menu(clear_db, insert_menu):
    test_response_payload = [{"id": '', "title": "My menu 1",
                              "description": "My menu description 1", "submenus_count": 0, "dishes_count": 0}]

    test_response_payload[0]['id'] = insert_menu(test_response_payload[0]['title'],
                                                 test_response_payload[0]['description']).id
    response = client.get('/api/v1/menus')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_menu(clear_db, insert_menu):
    test_response_payload = {"id": '', "title": "My menu 1", "description": "My menu description 1",
                             "submenus_count": 0, "dishes_count": 0}
    test_response_payload['id'] = insert_menu(test_response_payload['title'],
                                              test_response_payload['description']).id
    response = client.get(f'/api/v1/menus/{test_response_payload["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_menu_not_found(clear_db):
    test_response_payload = {"detail": "menu not found"}
    response = client.get('/api/v1/menus/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_patch_menu(clear_db, insert_menu):
    test_response_payload = {"id": '', "title": "My updated menu 1", "description": "My updated menu description 1",
                             "submenus_count": 0, "dishes_count": 0}
    test_response_payload['id'] = insert_menu(test_response_payload['title'],
                                              test_response_payload['description']).id
    response = client.get(f'/api/v1/menus/{test_response_payload["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_patch_menu_not_found(clear_db):
    test_response_payload = {"detail": "menu not found"}
    response = client.get('/api/v1/menus/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_delete_menu(clear_db, insert_menu):
    test_response_payload = {"status": True, "message": "The menu has been deleted"}
    test_menu = {"id": '', "title": "My updated menu 1", "description": "My updated menu description 1",
                 "submenus_count": 0, "dishes_count": 0}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    response = client.delete(f'/api/v1/menus/{test_menu["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_delete_menu_not_found(clear_db, insert_menu):
    test_response_payload = {"status": False, "message": "menu not found"}
    response = client.delete('/api/v1/menus/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload
