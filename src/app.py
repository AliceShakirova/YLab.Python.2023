from fastapi import BackgroundTasks, FastAPI
from starlette.responses import JSONResponse

from src import service
from src.Entities.dish import Dish, DishCreateModel, DishListModel, DishModel
from src.Entities.menu import Menu, MenuCreateModel, MenuListModel, MenuModel
from src.Entities.submenu import (
    Submenu,
    SubmenuCreateModel,
    SubmenuListModel,
    SubmenuModel,
)

app = FastAPI()

# menu


@app.on_event('startup')
async def init():
    await service.init()


@app.get('/api/v1/menus/all', response_model=list)
async def get_all_menus_submenus_and_dishes() -> list:
    return await service.get_all_menus_submenus_and_dishes()


@app.get('/api/v1/menus', response_model=MenuListModel)
async def get_list_menus() -> list[type[Menu]] | list[MenuModel]:
    return await service.get_all_menus()


@app.post('/api/v1/menus', response_model=MenuModel, status_code=201)
async def post_menu(menu: MenuCreateModel, background_tasks: BackgroundTasks) -> Menu | MenuModel:
    return await service.post_menu(menu, background_tasks)


@app.get('/api/v1/menus/{menu_id}', response_model=MenuModel)
async def get_target_menu(menu_id: str) -> MenuModel | JSONResponse:
    menu = await service.get_menu(menu_id)
    if not menu:
        return JSONResponse({'detail': 'menu not found'}, 404)
    else:
        return menu


@app.patch('/api/v1/menus/{menu_id}', response_model=MenuModel)
async def patch_menu(menu_id: str, menu: MenuCreateModel, background_tasks: BackgroundTasks) -> MenuModel | JSONResponse:
    updated_menu = await service.patch_menu(menu_id, menu, background_tasks)
    if not updated_menu:
        return JSONResponse({'detail': 'menu not found'}, 404)
    else:
        return updated_menu


@app.delete('/api/v1/menus/{menu_id}')
async def delete_menu(menu_id: str, background_tasks: BackgroundTasks) -> JSONResponse:
    result_of_delete = await service.delete_menu(menu_id, background_tasks)
    if not result_of_delete:
        return JSONResponse({'status': result_of_delete, 'message': 'menu not found'}, 404)
    else:
        return JSONResponse({'status': result_of_delete, 'message': 'The menu has been deleted'}, 200)

# submenu


@app.get('/api/v1/menus/{menu_id}/submenus', response_model=SubmenuListModel)
async def get_list_submenus(menu_id: str) -> list[Submenu] | list[SubmenuModel]:
    return await service.get_all_submenus(menu_id)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubmenuModel)
async def get_target_submenu(menu_id: str, submenu_id: str) -> SubmenuModel | JSONResponse:
    submenu = await service.get_submenu(menu_id, submenu_id)
    if not submenu:
        return JSONResponse({'detail': 'submenu not found'}, 404)
    else:
        return submenu


@app.post('/api/v1/menus/{menu_id}/submenus', response_model=SubmenuModel, status_code=201)
async def post_submenu(menu_id: str, submenu: SubmenuCreateModel, background_tasks: BackgroundTasks) -> Submenu | SubmenuModel:
    return await service.post_submenu(menu_id, submenu, background_tasks)


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubmenuModel)
async def patch_submenu(menu_id: str, submenu_id: str, submenu: SubmenuCreateModel,
                        background_tasks: BackgroundTasks) -> Submenu | SubmenuModel | JSONResponse:
    updated_submenu = await service.patch_submenu(menu_id, submenu_id, submenu, background_tasks)
    if not updated_submenu:
        return JSONResponse({'detail': 'submenu not found'}, 404)
    else:
        return updated_submenu


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def delete_submenu(menu_id: str, submenu_id: str, background_tasks: BackgroundTasks) -> JSONResponse:
    result_of_delete = await service.delete_submenu(menu_id, submenu_id, background_tasks)
    if not result_of_delete:
        return JSONResponse({'status': result_of_delete, 'message': 'submenu not found'}, 404)
    else:
        return JSONResponse({'status': result_of_delete, 'message': 'The submenu has been deleted'},
                            200)

# dish


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishListModel)
async def get_list_dishes(menu_id: str, submenu_id: str) -> list[type[Dish]] | list[DishModel] | None:
    return await service.get_all_dishes(menu_id, submenu_id)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
async def get_target_dish(menu_id: str, submenu_id: str, dish_id: str) -> Dish | JSONResponse:
    dish = await service.get_dish(menu_id, submenu_id, dish_id)
    if dish is None:
        return JSONResponse({'detail': 'dish not found'}, 404)
    else:
        return dish


@app.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishModel, status_code=201)
async def post_dish(menu_id: str, submenu_id: str, dish: DishCreateModel,
                    background_tasks: BackgroundTasks) -> Dish | DishModel | JSONResponse:
    new_dish = await service.post_dish(menu_id, submenu_id, dish, background_tasks)
    if not new_dish:
        return JSONResponse({'detail': 'submenu not found'}, 404)
    else:
        return new_dish


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
async def patch_dish(menu_id: str, submenu_id: str, dish_id: str, dish: DishCreateModel,
                     background_tasks: BackgroundTasks) -> Dish | DishModel | JSONResponse:
    updated_dish = await service.patch_dish(menu_id, submenu_id, dish_id, dish, background_tasks)
    if not updated_dish:
        return JSONResponse({'detail': 'dish not found'}, 404)
    else:
        return updated_dish


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def delete_dish(menu_id: str, submenu_id: str, dish_id: str, background_tasks: BackgroundTasks) -> JSONResponse:
    result_of_delete = await service.delete_dish(menu_id, submenu_id, dish_id, background_tasks)
    if not result_of_delete:
        return JSONResponse({'status': result_of_delete, 'message': 'dish not found'}, 404)
    else:
        return JSONResponse({'status': result_of_delete, 'message': 'The dish has been deleted'}, 200)
