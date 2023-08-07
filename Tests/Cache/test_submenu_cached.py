from starlette.testclient import TestClient

from conftest import func_reverse
from src.app import app

client = TestClient(app)


def test_get_all_submenu_empty(clear_storage, insert_menu, insert_menu_cache):
    test_response_payload = []
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 0,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    response = client.get(url=func_reverse('get_list_submenus', menu_id=test_menu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_post_submenu(clear_storage, insert_menu, insert_menu_cache):
    test_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = {'id': '', 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    response = client.post(url=func_reverse('post_submenu', menu_id=test_menu['id']), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


def test_get_all_submenu(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache):
    test_response_payload = [{'id': '', 'title': 'My submenu 1',
                              'description': 'My submenu description 1', 'dishes_count': 0}]
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_response_payload[0]['id'] = insert_submenu(title=test_response_payload[0]['title'],
                                                    description=test_response_payload[0]['description'],
                                                    menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_response_payload[0]['id'], title=test_response_payload[0]['title'],
                         description=test_response_payload[0]['description'], menu_id=test_menu['id'],
                         dishes_count=test_response_payload[0]['dishes_count'])
    response = client.get(url=func_reverse('get_list_submenus', menu_id=test_menu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_submenu(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache):
    test_response_payload = {'id': '', 'title': 'My submenu 1', 'description': 'My submenu description 1',
                             'dishes_count': 0}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_response_payload['id'] = insert_submenu(title=test_response_payload['title'],
                                                 description=test_response_payload['description'],
                                                 menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_response_payload['id'], title=test_response_payload['title'],
                         description=test_response_payload['description'], menu_id=test_menu['id'],
                         dishes_count=test_response_payload['dishes_count'])
    response = client.get(url=func_reverse('get_target_submenu', menu_id=test_menu['id'],
                                           submenu_id=test_response_payload['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_get_target_submenu_not_found(clear_storage, insert_menu, insert_menu_cache):
    test_response_payload = {'detail': 'submenu not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    response = client.get(url=func_reverse('get_target_submenu', menu_id=test_menu['id'],
                                           submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_patch_submenu(clear_storage, insert_menu, insert_menu_cache, insert_submenu, insert_submenu_cache):
    test_response_payload = {'id': '', 'title': 'My updated submenu 1',
                             'description': 'My updated submenu description 1', 'dishes_count': 0}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_response_payload['id'] = insert_submenu(title=test_response_payload['title'],
                                                 description=test_response_payload['description'],
                                                 menu_id=test_menu['id']).id
    insert_submenu_cache(submenu_id=test_response_payload['id'], title=test_response_payload['title'],
                         description=test_response_payload['description'], menu_id=test_menu['id'],
                         dishes_count=test_response_payload['dishes_count'])
    response = client.get(url=func_reverse('patch_submenu', menu_id=test_menu['id'],
                                           submenu_id=test_response_payload['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_patch_submenu_not_found(clear_storage, insert_menu, insert_menu_cache):
    test_response_payload = {'detail': 'submenu not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    response = client.get(url=func_reverse('patch_submenu', menu_id=test_menu['id'],
                                           submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


def test_delete_submenu(clear_storage, insert_menu, insert_submenu, insert_menu_cache):
    test_response_payload = {'status': True, 'message': 'The submenu has been deleted'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 1,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    test_submenu = {'id': '', 'title': 'My updated submenu 1', 'description': 'My updated submenu description 1',
                    'dishes_count': 0}
    test_submenu['id'] = insert_submenu(title=test_submenu['title'], description=test_submenu['description'],
                                        menu_id=test_menu['id']).id
    response = client.delete(url=func_reverse('delete_submenu', menu_id=test_menu['id'],
                                              submenu_id=test_submenu['id']))
    assert response.status_code == 200
    assert response.json() == test_response_payload


def test_delete_submenu_not_found(clear_storage, insert_menu, insert_menu_cache):
    test_response_payload = {'status': False, 'message': 'submenu not found'}
    test_menu = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1', 'submenus_count': 0,
                 'dishes_count': 0}
    test_menu['id'] = insert_menu(title=test_menu['title'], description=test_menu['description']).id
    insert_menu_cache(menu_id=test_menu['id'], title=test_menu['title'], description=test_menu['description'],
                      submenus_count=test_menu['submenus_count'], dishes_count=test_menu['dishes_count'])
    response = client.delete(url=func_reverse('delete_submenu', menu_id=test_menu['id'],
                                              submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload
