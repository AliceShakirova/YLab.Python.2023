from typing import Callable

import pytest
from _decimal import Decimal
from async_asgi_testclient import TestClient
from fastapi.encoders import jsonable_encoder

import conftest
from conftest import func_reverse
from src.app import app
from src.Entities.dish import Dish
from src.Entities.menu import Menu, MenuModel
from src.Entities.submenu import Submenu

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_all_inst(clear_storage: Callable, insert_full_menu: Callable) -> None:
    menu_1: Menu = Menu(id='a2eb416c-2245-4526-bb4b-6343d5c5016f', title='My menu 1',
                        description='My menu description 1')
    submenu_1: Submenu = Submenu(id='bc19488a-cc0e-4eaa-8d21-4d486a45392f', title='My submenu 1',
                                 description='My submenu description 1', menu_id=menu_1.id)
    submenu_2: Submenu = Submenu(id='602033b3-0462-4de1-a2f8-d8494795e0c0', title='My submenu 2',
                                 description='My submenu description 2', menu_id=menu_1.id)
    dish_1: Dish = Dish(id='bc19488a-cc0e-4eaa-8d21-4d486a45392f', title='My dish 1',
                        description='My dish description 1', submenu_id=submenu_1.id, price=Decimal(12.5))
    dish_2: Dish = Dish(id='ded236d9-e931-496f-902b-91fbaf9f5d65', title='My dish 2',
                        description='My dish description 2', submenu_id=submenu_1.id, price=Decimal(15.5))
    dish_3: Dish = Dish(id='c6dbcd4b-10a4-41d7-8b26-20e08c7cfe9a', title='My dish 3',
                        description='My dish description 3', submenu_id=submenu_2.id, price=Decimal(13.55))
    menu_1.submenus.extend([submenu_1, submenu_2])
    submenu_1.dishes.extend([dish_1, dish_2])
    submenu_2.dishes.append(dish_3)
    await insert_full_menu(menu_1)
    response = await client.get(func_reverse('get_all_menus_submenus_and_dishes'))
    assert response.status_code == 200
    assert response.json() == jsonable_encoder([menu_1])


@pytest.mark.asyncio
async def test_get_all_menu_empty_storage(clear_storage: Callable) -> None:
    test_response_payload: list = []
    response = await client.get(func_reverse('get_list_menus'))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_post_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My menu 1', 'description': 'My menu description 1'}
    test_response_payload = await insert_inst(Menu, storage=conftest.NOT_ADD)
    response = await client.post(func_reverse('post_menu'), json=test_request_payload)
    assert response.status_code == 201
    test_response_payload.id = response.json()['id']
    model: MenuModel = MenuModel.model_validate(response.json(), from_attributes=True)  # type: ignore
    assert model == test_response_payload


@pytest.mark.asyncio
async def test_get_all_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = [{'id': '', 'title': 'My menu 1',
                              'description': 'My menu description 1', 'submenus_count': 0, 'dishes_count': 0}]
    test_response_payload[0]['id'] = (await insert_inst(Menu, storage=conftest.ADD_TO_DB)).id
    response = await client.get(func_reverse('get_list_menus'))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_get_target_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = {'id': '', 'title': 'My menu 1', 'description': 'My menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.get(func_reverse('get_target_menu', menu_id=test_menu.id))
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id'] = test_menu.id
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_get_target_menu_not_found(clear_storage: Callable) -> None:
    test_response_payload = {'detail': 'menu not found'}
    response = await client.get(func_reverse('get_target_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_patch_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_request_payload = {'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                            'submenus_count': 0, 'dishes_count': 0}
    test_response_payload = {'id': '', 'title': 'My updated menu 1', 'description': 'My updated menu description 1',
                             'submenus_count': 0, 'dishes_count': 0}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.patch(func_reverse('patch_menu', menu_id=test_menu.id), json=test_request_payload)
    assert response.status_code == 200
    test_response_payload['id'] = response.json()['id']
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_patch_menu_not_found(clear_storage: Callable) -> None:
    test_response_payload = {'detail': 'menu not found'}
    response = await client.get(func_reverse('patch_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_delete_menu(clear_storage: Callable, insert_inst: Callable) -> None:
    test_response_payload = {'status': True, 'message': 'The menu has been deleted'}
    test_menu = await insert_inst(Menu, storage=conftest.ADD_TO_DB)
    response = await client.delete(func_reverse('delete_menu', menu_id=test_menu.id))
    assert response.status_code == 200
    assert response.json() == test_response_payload


@pytest.mark.asyncio
async def test_delete_menu_not_found(clear_storage: Callable) -> None:
    test_response_payload = {'status': False, 'message': 'menu not found'}
    response = await client.delete(func_reverse('delete_menu', menu_id='a2eb416c-2245-4526-bb4b-6343d5c5016f'))
    assert response.status_code == 404
    assert response.json() == test_response_payload
