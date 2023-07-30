from starlette.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_all_dish_empty(clear_db, insert_menu, insert_submenu):
    test_response_payload = []
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My submenu 1", "description": "My submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu["id"]).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}/dishes')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_post_dish(clear_db, insert_menu, insert_submenu):
    test_request_payload = {"title": "My dish 1", "description": "My dish description 1", "price": "12.50"}
    test_response_payload = {"id": '', "title": "My dish 1", "description": "My dish description 1", "price": "12.50"}
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My submenu 1", "description": "My submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu["id"]).id
    response = client.post(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}/dishes',
                           json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_get_all_dish(clear_db, insert_menu, insert_submenu, insert_dish):
    test_response_payload = [{"id": '', "title": "My dish 1", "description": "My dish description 1", "price": "12.50"}]
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My submenu 1", "description": "My submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu["id"]).id
    test_response_payload[0]['id'] = insert_dish(test_response_payload[0]['title'],
                                                 test_response_payload[0]['description'],
                                                 test_submenu["id"], test_response_payload[0]["price"]).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}/dishes')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_dish(clear_db, insert_menu, insert_submenu, insert_dish):
    test_response_payload = {"id": '', "title": "My dish 1", "description": "My dish description 1", "price": "12.50"}
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My submenu 1", "description": "My submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu["id"]).id
    test_response_payload['id'] = insert_dish(test_response_payload['title'], test_response_payload['description'],
                                              test_submenu["id"], test_response_payload['price']).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}/'
                          f'dishes/{test_response_payload["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_dish_not_found(clear_db, insert_menu, insert_submenu):
    test_response_payload = {"detail": "dish not found"}
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My submenu 1", "description": "My submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu["id"]).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}'
                          f'/dishes/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_patch_dish(clear_db, insert_menu, insert_submenu, insert_dish):
    test_response_payload = {"id": '', "title": "My updated dish 1", "description": "My updated dish description 1",
                             "price": "14.50"}
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My submenu 1", "description": "My submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu["id"]).id
    test_response_payload['id'] = insert_dish(test_response_payload['title'],
                                              test_response_payload['description'], test_submenu['id'],
                                              test_response_payload['price']).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}/dishes/{test_response_payload["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_patch_dish_not_found(clear_db, insert_menu, insert_submenu):
    test_response_payload = {"detail": "dish not found"}
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My submenu 1", "description": "My submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu["id"]).id
    response = client.get(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}/'
                          f'dishes/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_delete_dish(clear_db, insert_menu, insert_submenu, insert_dish):
    test_response_payload = {"status": True, "message": "The dish has been deleted"}
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My updated submenu 1", "description": "My updated submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu['id']).id
    test_dish = {"id": '', "title": "My dish 1", "description": "My dish description 1", "price": "12.50"}
    test_dish['id'] = insert_dish(test_dish['title'], test_dish['description'], test_submenu["id"],
                                  test_dish["price"]).id
    response = client.delete(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}/'
                             f'dishes/{test_dish["id"]}')
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_delete_dish_not_found(clear_db, insert_menu, insert_submenu):
    test_response_payload = {"status": False, "message": "dish not found"}
    test_menu = {"id": '', "title": "My menu 1", "description": "My menu description 1"}
    test_menu['id'] = insert_menu(test_menu['title'], test_menu['description']).id
    test_submenu = {"id": '', "title": "My updated submenu 1", "description": "My updated submenu description 1"}
    test_submenu['id'] = insert_submenu(test_submenu['title'], test_submenu['description'], test_menu['id']).id
    response = client.delete(f'/api/v1/menus/{test_menu["id"]}/submenus/{test_submenu["id"]}/'
                             f'dishes/"a2eb416c-2245-4526-bb4b-6343d5c5016f"')
    assert response.status_code == 404
    assert response.json() == test_response_payload
