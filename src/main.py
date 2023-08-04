import fastapi
from starlette.responses import JSONResponse

from src import service
from src.Entities.dish import DishCreateModel, DishListModel, DishModel
from src.Entities.menu import MenuCreateModel, MenuListModel, MenuModel
from src.Entities.submenu import SubmenuCreateModel, SubmenuListModel, SubmenuModel

app = fastapi.FastAPI()

# menu


@app.get('/api/v1/menus', response_model=MenuListModel)
def get_list_menus():
    return service.get_all_menus()


@app.post('/api/v1/menus', response_model=MenuModel, status_code=201)
def post_menu(menu: MenuCreateModel):
    return service.post_menu(menu=menu)


@app.get('/api/v1/menus/{menu_id}', response_model=MenuModel)
def get_target_menu(menu_id):
    menu = service.get_menu(menu_id)
    if not menu:
        return JSONResponse({'detail': 'menu not found'}, 404)
    else:
        return menu


@app.patch('/api/v1/menus/{menu_id}', response_model=MenuModel)
def patch_menu(menu_id, menu: MenuCreateModel):
    updated_menu = service.patch_menu(menu_id, menu)
    if not updated_menu:
        return JSONResponse({'detail': 'menu not found'}, 404)
    else:
        return updated_menu


@app.delete('/api/v1/menus/{menu_id}')
def delete_menu(menu_id):
    result_of_delete = service.delete_menu(menu_id)
    if not result_of_delete:
        return JSONResponse({'status': result_of_delete, 'message': 'menu not found'}, 404)
    else:
        return JSONResponse({'status': result_of_delete, 'message': 'The menu has been deleted'}, 200)

# submenu


@app.get('/api/v1/menus/{menu_id}/submenus', response_model=SubmenuListModel)
def get_list_submenus(menu_id):
    return service.get_all_submenus(menu_id)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubmenuModel)
def get_target_submenu(menu_id, submenu_id):
    submenu = service.get_submenu(menu_id, submenu_id)
    if not submenu:
        return JSONResponse({'detail': 'submenu not found'}, 404)
    else:
        return submenu


@app.post('/api/v1/menus/{menu_id}/submenus', response_model=SubmenuModel, status_code=201)
def post_submenu(menu_id, submenu: SubmenuCreateModel):
    return service.post_submenu(menu_id, submenu)


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubmenuModel)
def patch_submenu(menu_id, submenu_id, submenu: SubmenuCreateModel):
    updated_submenu = service.patch_submenu(menu_id, submenu_id, submenu)
    if not updated_submenu:
        return JSONResponse({'detail': 'submenu not found'}, 404)
    else:
        return updated_submenu


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
def delete_submenu(menu_id, submenu_id):
    result_of_delete = service.delete_submenu(menu_id, submenu_id)
    if not result_of_delete:
        return JSONResponse({'status': result_of_delete, 'message': 'submenu not found'}, 404)
    else:
        return JSONResponse({'status': result_of_delete, 'message': 'The submenu has been deleted'},
                            200)

# dish


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishListModel)
def get_list_dishes(menu_id, submenu_id):
    return service.get_all_dishes(menu_id, submenu_id)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
def get_target_dish(menu_id, submenu_id, dish_id):
    dish = service.get_dish(menu_id, submenu_id, dish_id)
    if not dish:
        return JSONResponse({'detail': 'dish not found'}, 404)
    else:
        return dish


@app.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishModel, status_code=201)
def post_dish(menu_id, submenu_id, dish: DishCreateModel):
    new_dish = service.post_dish(menu_id, submenu_id, dish)
    if not new_dish:
        return JSONResponse({'detail': 'submenu not found'}, 404)
    else:
        return new_dish


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
def patch_dish(menu_id, submenu_id, dish_id, dish: DishCreateModel):
    updated_dish = service.patch_dish(menu_id, submenu_id, dish_id, dish)
    if not updated_dish:
        return JSONResponse({'detail': 'dish not found'}, 404)
    else:
        return updated_dish


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def delete_dish(menu_id, submenu_id, dish_id):
    result_of_delete = service.delete_dish(menu_id, submenu_id, dish_id)
    if not result_of_delete:
        return JSONResponse({'status': result_of_delete, 'message': 'dish not found'}, 404)
    else:
        return JSONResponse({'status': result_of_delete, 'message': 'The dish has been deleted'}, 200)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
