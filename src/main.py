import os

import fastapi
from src.Db.database import Database
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from src.Entities.dish import DishModel, DishCreateModel, DishListModel
from src.Entities.menu import MenuModel, MenuCreateModel, MenuListModel
from src.Entities.submenu import SubmenuModel, SubmenuCreateModel, SubmenuListModel


app = fastapi.FastAPI()

db_address = os.getenv('db_address')
if db_address is None:
    db_address = 'localhost'

db = Database('postgres', 'qwerty', db_address, 5432, 'mydb')

repo_m = db.repo_m
repo_s = db.repo_s
repo_d = db.repo_d

# menu


@app.get("/api/v1/menus", response_model=MenuListModel)
def get_list_menus():
    all_menus = repo_m.get_all_menus()
    if not all_menus:
        return JSONResponse(content=[], status_code=200)
    for menu in all_menus:
        menu.submenus_count, menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu.id)
    return all_menus


@app.post('/api/v1/menus', response_model=MenuModel, status_code=201)
def post_menu(menu: MenuCreateModel):
    new_menu = repo_m.create_menu(title=menu.title, description=menu.description)
    new_menu.submenus_count, new_menu.dishes_count = 0, 0
    return new_menu


@app.get('/api/v1/menus/{menu_id}', response_model=MenuModel)
def get_target_menu(menu_id):
    menu = repo_m.get_menu(menu_id=menu_id)
    if not menu:
        return JSONResponse({"detail": "menu not found"}, status_code=404)
    menu.submenus_count, menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu.id)
    return menu


@app.patch('/api/v1/menus/{menu_id}', response_model=MenuModel)
def patch_menu(menu_id, menu: MenuCreateModel):
    updated_menu = repo_m.update_menu(menu_id=menu_id, title=menu.title, description=menu.description)
    if not updated_menu:
        return JSONResponse(content={"detail": "menu not found"}, status_code=404)
    updated_menu.submenus_count, updated_menu.dishes_count = repo_m.get_submenus_and_dishes_counts(menu.id)
    return updated_menu


@app.delete('/api/v1/menus/{menu_id}')
def delete_menu(menu_id):
    deleted = repo_m.delete_menu(menu_id=menu_id)
    if not deleted:
        return JSONResponse(content={'status': deleted, "message": "menu not found"}, status_code=404)
    json = jsonable_encoder({'status': deleted, "message": "The menu has been deleted"})
    return JSONResponse(content=json, status_code=200)

# submenu


@app.get('/api/v1/menus/{menu_id}/submenus', response_model=SubmenuListModel)
def get_list_submenus(menu_id):
    submenus = repo_s.get_submenus_of_menu(menu_id)
    if not submenus:
        return JSONResponse(content=[], status_code=200)
    for submenu in submenus:
        submenu.dishes_count = repo_d.get_dishes_count(submenu.id)
    return submenus


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubmenuModel)
def get_target_submenu(menu_id, submenu_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=404)
    submenu.dishes_count = repo_d.get_dishes_count(submenu.id)
    return submenu


@app.post('/api/v1/menus/{menu_id}/submenus', response_model=SubmenuModel, status_code=201)
def post_submenu(menu_id, submenu: SubmenuCreateModel):
    new_submenu = repo_s.create_submenu(title=submenu.title, description=submenu.description, menu_id=menu_id)
    new_submenu.dishes_count = 0
    return new_submenu


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=SubmenuModel)
def patch_submenu(menu_id, submenu_id, submenu: SubmenuCreateModel):
    updated_submenu = repo_s.update_submenu(submenu_id=submenu_id, title=submenu.title,
                                            description=submenu.description, menu_id=menu_id)
    if not updated_submenu:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=404)
    updated_submenu.dishes_count = repo_d.get_dishes_count(updated_submenu.id)
    return updated_submenu


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
def delete_submenu(menu_id, submenu_id):
    deleted = repo_s.delete_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not deleted:
        return JSONResponse(content={'status': deleted, "message": "submenu not found"}, status_code=404)
    json = jsonable_encoder({'status': deleted, "message": "The submenu has been deleted"})
    return JSONResponse(content=json, status_code=200)

# dish


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishListModel)
def get_list_dishes(menu_id, submenu_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content=[], status_code=200)
    dishes = repo_d.get_dishes_of_submenu(submenu_id=submenu_id)
    return dishes


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
def get_target_dish(menu_id, submenu_id, dish_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)
    dish = repo_d.get_dish(submenu_id=submenu_id, dish_id=dish_id)
    if not dish:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)
    return dish


@app.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishModel, status_code=201)
def post_dish(menu_id, submenu_id, dish: DishCreateModel):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=404)
    new_dish = repo_d.create_dish(title=dish.title, description=dish.description, submenu_id=submenu_id,
                                  price=dish.price)
    return new_dish


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishModel)
def patch_dish(menu_id, submenu_id, dish_id, dish: DishCreateModel):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)
    updated_dish = repo_d.update_dish(dish_id=dish_id, title=dish.title, description=dish.description,
                                      submenu_id=submenu_id, price=dish.price)
    if not updated_dish:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)
    return updated_dish


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def delete_dish(menu_id, submenu_id, dish_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={'status': False, "detail": "dish not found"}, status_code=404)
    deleted = repo_d.delete_dish(dish_id=dish_id, submenu_id=submenu_id)
    if not deleted:
        return JSONResponse(content={'status': deleted, "message": "dish not found"}, status_code=404)
    json = jsonable_encoder({'status': deleted, "message": "The dish has been deleted"})
    return JSONResponse(content=json, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
