import fastapi
from starlette.responses import JSONResponse

from src import service
from src.Entities.dish import DishModel, DishCreateModel, DishListModel
from src.Entities.menu import MenuModel, MenuCreateModel, MenuListModel
from src.Entities.submenu import SubmenuModel, SubmenuCreateModel, SubmenuListModel

app = fastapi.FastAPI()

# menu


@app.get("/api/v1/menus", response_model=MenuListModel)
def get_list_menus():
    return service.get_all_menus()


@app.post('/api/v1/menus', response_model=MenuModel, status_code=201)
def post_menu(menu: MenuCreateModel):
    return service.post_menu(menu=menu)


@app.get('/api/v1/menus/{menu_id}', response_model=MenuModel)
def get_target_menu(menu_id):
    result = service.get_menu(menu_id)
    if not result:
        return JSONResponse({"detail": "menu not found"}, 404)
    else:
        return result


@app.patch('/api/v1/menus/{menu_id}', response_model=MenuModel)
def patch_menu(menu_id, menu: MenuCreateModel):
    result = service.patch_menu(menu_id, menu)
    if not result:
        return JSONResponse({"detail": "menu not found"}, 404)
    else:
        return result


@app.delete('/api/v1/menus/{menu_id}')
def delete_menu(menu_id):
    result = service.delete_menu(menu_id)
    if not result:
        return JSONResponse({'status': result, "message": "menu not found"}, 404)
    else:
        return JSONResponse({'status': result, "message": "The menu has been deleted"}, 200)

# submenu


@app.get('/api/v1/menus/{menu_id}/submenus', response_model=SubmenuListModel)
def get_list_submenus(menu_id):
    return service.get_all_submenus(menu_id)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubmenuModel)
def get_target_submenu(menu_id, submenu_id):
    result = service.get_submenu(menu_id, submenu_id)
    if not result:
        return JSONResponse({"detail": "submenu not found"}, 404)
    else:
        return result


@app.post('/api/v1/menus/{menu_id}/submenus', response_model=SubmenuModel, status_code=201)
def post_submenu(menu_id, submenu: SubmenuCreateModel):
    return service.post_submenu(menu_id, submenu)


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubmenuModel)
def patch_submenu(menu_id, submenu_id, submenu: SubmenuCreateModel):
    result = service.patch_submenu(menu_id, submenu_id, submenu)
    if not result:
        return JSONResponse({"detail": "submenu not found"}, 404)
    else:
        return result


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
def delete_submenu(menu_id, submenu_id):
    result = service.delete_submenu(menu_id, submenu_id)
    if not result:
        return JSONResponse({'status': result, "message": "submenu not found"}, 404)
    else:
        return JSONResponse({'status': result, "message": "The submenu has been deleted"}, 200)

# dish


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishListModel)
def get_list_dishes(menu_id, submenu_id):
    return service.get_all_dishes(menu_id, submenu_id)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
def get_target_dish(menu_id, submenu_id, dish_id):
    result = service.get_dish(menu_id, submenu_id, dish_id)
    if not result:
        return JSONResponse({"detail": "dish not found"}, 404)
    else:
        return result


@app.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishModel, status_code=201)
def post_dish(menu_id, submenu_id, dish: DishCreateModel):
    result = service.post_dish(menu_id, submenu_id, dish)
    if not result:
        return JSONResponse({"detail": "submenu not found"}, 404)
    else:
        return result


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
def patch_dish(menu_id, submenu_id, dish_id, dish: DishCreateModel):
    result = service.patch_dish(menu_id, submenu_id, dish_id, dish)
    if not result:
        return JSONResponse({"detail": "dish not found"}, 404)
    else:
        return result


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def delete_dish(menu_id, submenu_id, dish_id):
    result = service.delete_dish(menu_id, submenu_id, dish_id)
    if not result:
        return JSONResponse({'status': result, "message": "dish not found"}, 404)
    else:
        return JSONResponse({'status': result, "message": "The dish has been deleted"}, 200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
