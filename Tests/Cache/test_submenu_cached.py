from starlette.testclient import TestClient

import conftest
from conftest import func_reverse
from src.app import app
from src.Cache.caches import MenuCache, SubmenuCache
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu, SubmenuModel

client = TestClient(app)


def test_get_all_submenu_empty(clear_storage, insert_inst):
    test_response_payload = []
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_CACHE)
    response = client.get(url=func_reverse('get_list_submenus', menu_id=test_menu['id']))
    assert response.status_code == 200
    test_all_submenus = SubmenuCache.get_submenus(test_menu['id'])
    assert test_all_submenus == test_response_payload
    test_menu = MenuCache.get_menu(test_menu['id'])
    assert test_menu.submenus_count == 0


def test_post_submenu(clear_storage, insert_inst):  # type: ignore
    test_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = {'id': '', 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_CACHE)
    response = client.post(url=func_reverse('post_submenu', menu_id=test_menu['id']), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload['id'] = response.json()['id']
    test_submenu_cache = SubmenuCache.get_submenu(test_response_payload['id'])
    test_submenu: SubmenuModel = SubmenuModel.model_validate(  # type: ignore
        test_response_payload, from_attributes=True)  # type: ignore
    assert test_submenu_cache == test_submenu
    test_menu = MenuCache.get_menu(test_menu['id'])
    assert test_menu.submenus_count == 1


def test_get_all_submenu(clear_storage, insert_inst):
    test_submenu_request_payload = {'title': 'My submenu 1', 'description': 'My submenu description 1'}
    test_response_payload = [{'id': '', 'title': 'My submenu 1',
                             'description': 'My submenu description 1', 'dishes_count': 0}]
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_CACHE)
    client.post(url=func_reverse('post_submenu', menu_id=test_menu['id']),
                json=test_submenu_request_payload)
    response = client.get(url=func_reverse('get_list_submenus', menu_id=test_menu['id']))
    assert response.status_code == 200
    test_response_payload[0]['id'] = response.json()[0]['id']
    test_all_submenus = SubmenuCache.get_submenus(test_menu['id'])
    test_response_payload[0]: SubmenuModel = SubmenuModel.model_validate(  # type: ignore
        test_response_payload[0], from_attributes=True)  # type: ignore
    assert test_all_submenus == test_response_payload
    test_menu = MenuCache.get_menu(test_menu['id'])
    assert test_menu.submenus_count == 1


def test_get_target_submenu(clear_storage, insert_inst):
    test_menu, test_response_payload = insert_inst(Submenu, updated=False, storage=conftest.ADD_TO_CACHE)
    response = client.get(url=func_reverse('get_target_submenu', menu_id=test_menu['id'],
                                           submenu_id=test_response_payload['id']))
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    test_submenu_cache = SubmenuCache.get_submenu(test_response_payload['id'])
    test_submenu: SubmenuModel = SubmenuModel.model_validate(  # type: ignore
        test_response_payload, from_attributes=True)  # type: ignore
    assert test_submenu_cache == test_submenu
    test_menu = MenuCache.get_menu(test_menu['id'])
    assert test_menu.submenus_count == 1


def test_get_target_submenu_not_found(clear_storage, insert_inst):
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_CACHE)
    response = client.get(url=func_reverse('get_target_submenu', menu_id=test_menu['id'],
                                           submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_submenu_cache = SubmenuCache.get_submenu('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_submenu_cache is None
    test_menu = MenuCache.get_menu(test_menu['id'])
    assert test_menu.submenus_count == 0


def test_patch_submenu(clear_storage, insert_inst):
    test_request_payload = {'title': 'My updated submenu 1', 'description': 'My updated submenu description 1'}
    test_response_payload = {'id': '', 'title': 'My updated submenu 1',
                             'description': 'My updated submenu description 1', 'dishes_count': 0}
    test_menu, test_submenu = insert_inst(Submenu, updated=False, storage=conftest.ADD_TO_CACHE)
    response = client.patch(url=func_reverse('patch_submenu', menu_id=test_menu['id'],
                                             submenu_id=test_submenu['id']), json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    test_submenu_cache = SubmenuCache.get_submenu(test_response_payload['id'])
    test_submenu: SubmenuModel = SubmenuModel.model_validate(  # type: ignore
        test_response_payload, from_attributes=True)  # type: ignore
    assert test_submenu_cache == test_submenu
    test_menu = MenuCache.get_menu(test_menu['id'])
    assert test_menu.submenus_count == 1


def test_patch_submenu_not_found(clear_storage, insert_inst):
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_CACHE)
    response = client.get(url=func_reverse('patch_submenu', menu_id=test_menu['id'],
                                           submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_submenu_cache = SubmenuCache.get_submenu('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_submenu_cache is None
    test_menu = MenuCache.get_menu(test_menu['id'])
    assert test_menu.submenus_count == 0


def test_delete_submenu(clear_storage, insert_inst):
    test_menu, test_submenu = insert_inst(Submenu, updated=False, storage=conftest.ADD_TO_CACHE)
    response = client.delete(url=func_reverse('delete_submenu', menu_id=test_menu['id'],
                                              submenu_id=test_submenu['id']))
    assert response.status_code == 200
    test_submenu_cache = SubmenuCache.get_submenu(test_submenu['id'])
    assert test_submenu_cache is None
    test_menu = MenuCache.get_menu(test_menu['id'])
    assert test_menu.submenus_count == 0


def test_delete_submenu_not_found(clear_storage, insert_inst):
    test_menu = insert_inst(Menu, updated=False, storage=conftest.ADD_TO_CACHE)
    response = client.delete(url=func_reverse('delete_submenu', menu_id=test_menu['id'],
                                              submenu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    test_submenu_cache = SubmenuCache.get_submenu('a2eb416c-2245-4526-bb4b-6343d5c5016f')
    assert test_submenu_cache is None
