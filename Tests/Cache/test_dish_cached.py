from starlette.testclient import TestClient

from conftest import func_reverse
from src.app import app

client = TestClient(app)


def test_get_all_dish_empty(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache):
    test_response_payload = []
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 1}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1', 'dishes_count': 1}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_submenu['title'],
                         description=test_submenu['description'], menu_id=test_menu['id'],
                         dishes_count=test_submenu['dishes_count'])
    response = client.get(url=func_reverse('get_list_dishes', menu_id=test_menu['id'],
                                           submenu_id=test_submenu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_post_dish(clear_storage, insert_menu_cache, insert_menu, insert_submenu_cache, insert_submenu):
    test_request_payload = {'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 1}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'],
                      dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1', 'dishes_count': 1}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_submenu['title'],
                         description=test_submenu['description'], menu_id=test_menu['id'],
                         dishes_count=test_submenu['dishes_count'])
    response = client.post(url=func_reverse('post_dish', menu_id=test_menu['id'],
                                            submenu_id=test_submenu['id']), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_get_all_dish(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache,
                      insert_dish, insert_dish_cache):
    test_response_payload = [{'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}]
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 1}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1', 'dishes_count': 1}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_submenu['title'], description=test_submenu['description'],
                         menu_id=test_menu['id'], dishes_count=test_submenu['dishes_count'])
    test_response_payload[0]['id'] = insert_dish(title=test_response_payload[0]['title'],
                                                 description=test_response_payload[0]['description'],
                                                 submenu_id=test_submenu['id'],
                                                 price=test_response_payload[0]['price']).id
    insert_dish_cache(dish_id=test_response_payload[0]['id'], title=test_response_payload[0]['title'],
                      description=test_response_payload[0]['description'],
                      menu_id=test_menu['id'],
                      submenu_id=test_submenu['id'],
                      price=test_response_payload[0]['price'])
    response = client.get(url=func_reverse('get_list_dishes', menu_id=test_menu['id'],
                                           submenu_id=test_submenu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_dish(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache,
                         insert_dish, insert_dish_cache):
    test_response_payload = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 1}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1', 'dishes_count': 1}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_submenu['title'],
                         description=test_submenu['description'], menu_id=test_menu['id'],
                         dishes_count=test_submenu['dishes_count'])
    test_response_payload['id'] = insert_dish(title=test_response_payload['title'],
                                              description=test_response_payload['description'],
                                              submenu_id=test_submenu['id'],
                                              price=test_response_payload['price']).id
    insert_dish_cache(dish_id=test_response_payload['id'], title=test_response_payload['title'],
                      description=test_response_payload['description'], menu_id=test_menu['id'],
                      submenu_id=test_submenu['id'],
                      price=test_response_payload['price'])
    response = client.get(url=func_reverse('get_target_dish', menu_id=test_menu['id'],
                                           submenu_id=test_submenu['id'], dish_id=test_response_payload['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_dish_not_found(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache):
    test_response_payload = {'detail': 'dish not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1', 'dishes_count': 0}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_submenu['title'],
                         description=test_submenu['description'], menu_id=test_menu['id'],
                         dishes_count=test_submenu['dishes_count'])
    response = client.get(url=func_reverse('get_target_dish', menu_id=test_menu['id'],
                                           submenu_id=test_submenu['id'],
                                           dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_patch_dish(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache,
                    insert_dish, insert_dish_cache):
    test_response_payload = {'id': '', 'title': 'My updated dish 1', 'description': 'My updated dish description 1',
                             'price': '14.50'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 1}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1', 'dishes_count': 1}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_submenu['title'],
                         description=test_submenu['description'], menu_id=test_menu['id'],
                         dishes_count=test_submenu['dishes_count'])
    test_response_payload['id'] = insert_dish(title=test_response_payload['title'],
                                              description=test_response_payload['description'],
                                              submenu_id=test_submenu['id'], price=test_response_payload['price']).id
    insert_dish_cache(dish_id=test_response_payload['id'], title=test_response_payload['title'],
                      description=test_response_payload['description'], menu_id=test_menu['id'],
                      submenu_id=test_submenu['id'],
                      price=test_response_payload['price'])
    response = client.get(url=func_reverse('patch_dish', menu_id=test_menu['id'],
                                           submenu_id=test_submenu['id'], dish_id=test_response_payload['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_patch_dish_not_found(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache):
    test_response_payload = {'detail': 'dish not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 1}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1', 'dishes_count': 1}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_submenu['title'],
                         description=test_submenu['description'], menu_id=test_menu['id'],
                         dishes_count=test_submenu['dishes_count'])
    response = client.get(url=func_reverse('patch_dish', menu_id=test_menu['id'],
                                           submenu_id=test_submenu['id'],
                                           dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_delete_dish(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache,
                     insert_dish, insert_dish_cache):
    test_response_payload = {'status': True, 'message': 'The dish has been deleted'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 1}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1', 'dishes_count': 1}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_submenu['title'],
                         description=test_submenu['description'], menu_id=test_menu['id'],
                         dishes_count=test_submenu['dishes_count'])
    test_dish = {'id': '', 'title': 'My dish 1', 'description': 'My dish description 1', 'price': '12.50'}
    test_dish['id'] = insert_dish(title=test_dish['title'], description=test_dish['description'],
                                  submenu_id=test_submenu['id'], price=test_dish['price']).id
    insert_dish_cache(dish_id=test_dish['id'], title=test_dish['title'], description=test_dish['description'],
                      menu_id=test_menu['id'], submenu_id=test_submenu['id'], price=test_dish['price'])
    response = client.delete(url=func_reverse('delete_dish', menu_id=test_menu['id'],
                                              submenu_id=test_submenu['id'], dish_id=test_dish['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_delete_dish_not_found(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache):
    test_response_payload = {'status': False, 'message': 'dish not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My updated submenu 1', 'description': 'My updated submenu description 1',
                    'menu_id': test_menu['id'], 'dishes_count': 1}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_submenu['id'], title=test_menu['title'], description=test_menu['description'],
                         menu_id=test_menu['id'], dishes_count=test_menu['dishes_count'])
    response = client.delete(url=func_reverse('delete_dish', menu_id=test_menu['id'],
                                              submenu_id=test_submenu['id'],
                                              dish_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload
