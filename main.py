from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
import fastapi
from starlette.responses import JSONResponse
import uvicorn
from sqlalchemy_utils import database_exists, create_database

from Entities.base import Base
from Repository import dish_repo, menu_repo, submenu_repo


SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:qwerty@db:5432/mydb'


if not database_exists(SQLALCHEMY_DATABASE_URL):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    create_database(engine.url)
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base.metadata.create_all(bind=engine)

repo_m = menu_repo.MenuRepo(engine)
repo_s = submenu_repo.SubmenuRepo(engine)
repo_d = dish_repo.DishRepo(engine)

app = fastapi.FastAPI()


def get_submenus_and_dishes_counts(menu_id):
    submenus = repo_s.get_submenus_of_menu(menu_id)
    submenus_count = len(submenus)
    dishes_count = len(repo_d.get_dishes_of_submenus(submenu.id for submenu in submenus))
    return submenus_count, dishes_count

# menu


@app.get("/api/v1/menus")
def get_list_menus():
    all_menus = repo_m.get_all_menus()
    if not all_menus:
        return JSONResponse(content=[], status_code=200)
    for menu in all_menus:
        menu.submenus_count, menu.dishes_count = get_submenus_and_dishes_counts(menu.id)
    json = jsonable_encoder(all_menus)
    return JSONResponse(content=json, status_code=200)


@app.post('/api/v1/menus')
def post_menu(title=fastapi.Body(embed=True), description=fastapi.Body(embed=True)):
    new_menu = repo_m.create_menu(title=title, description=description)
    data = repo_m.get_menu(new_menu)
    data.submenus_count, data.dishes_count = 0, 0
    json = jsonable_encoder(data)
    return JSONResponse(content=json, status_code=201)


@app.get('/api/v1/menus/{menu_id}')
def get_target_menu(menu_id):
    menu = repo_m.get_menu(menu_id=menu_id)
    if not menu:
        return JSONResponse({"detail": "menu not found"}, status_code=404)
    menu.submenus_count, menu.dishes_count = get_submenus_and_dishes_counts(menu.id)
    json = jsonable_encoder(menu)
    return JSONResponse(content=json, status_code=200)


@app.patch('/api/v1/menus/{menu_id}')
def patch_menu(menu_id, title=fastapi.Body(embed=True), description=fastapi.Body(embed=True)):
    updated_menu_id = repo_m.update_menu(menu_id=menu_id, title=title, description=description)
    if not updated_menu_id:
        return JSONResponse(content={"detail": "menu not found"}, status_code=404)
    menu = repo_m.get_menu(updated_menu_id)
    menu.submenus_count, menu.dishes_count = get_submenus_and_dishes_counts(menu_id=menu_id)
    json = jsonable_encoder(menu)
    return JSONResponse(content=json, status_code=200)


@app.delete('/api/v1/menus/{menu_id}')
def delete_menu(menu_id):
    deleted = repo_m.delete_menu(menu_id=menu_id)
    if not deleted:
        return JSONResponse(content={'status': deleted, "message": "menu not found"}, status_code=404)
    json = jsonable_encoder({'status': deleted, "message": "The menu has been deleted"})
    return JSONResponse(content=json, status_code=200)

# submenu


@app.get('/api/v1/menus/{menu_id}/submenus')
def get_list_submenus(menu_id):
    submenus = repo_s.get_submenus_of_menu(menu_id)
    if not submenus:
        return JSONResponse(content=[], status_code=200)
    for submenu in submenus:
        submenu.dishes_count = len(repo_d.get_dishes_of_submenu(submenu.id))
    json = jsonable_encoder(submenus)
    return JSONResponse(content=json, status_code=200)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
def get_target_submenu(menu_id, submenu_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=404)
    submenu.dishes_count = len(repo_d.get_dishes_of_submenu(submenu.id))
    json = jsonable_encoder(submenu)
    return JSONResponse(content=json, status_code=200)


@app.post('/api/v1/menus/{menu_id}/submenus')
def post_submenu(menu_id, title=fastapi.Body(embed=True), description=fastapi.Body(embed=True)):
    new_submenu_id = repo_s.create_submenu(title=title, description=description, menu_id=menu_id)
    data = repo_s.get_submenu(submenu_id=new_submenu_id, menu_id=menu_id)
    data.dishes_count = 0
    json = jsonable_encoder(data)
    return JSONResponse(content=json, status_code=201)


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
def patch_submenu(menu_id, submenu_id, title=fastapi.Body(embed=True), description=fastapi.Body(embed=True)):
    updated_submenu_id = repo_s.update_submenu(submenu_id=submenu_id, title=title, description=description,
                                               menu_id=menu_id)
    if not updated_submenu_id:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=404)
    submenu = repo_s.get_submenu(menu_id=menu_id, submenu_id=updated_submenu_id)
    submenu.dishes_count = len(repo_d.get_dishes_of_submenu(updated_submenu_id))
    json = jsonable_encoder(submenu)
    return JSONResponse(content=json, status_code=200)


@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
def delete_submenu(menu_id, submenu_id):
    deleted = repo_s.delete_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not deleted:
        return JSONResponse(content={'status': deleted, "message": "submenu not found"}, status_code=404)
    json = jsonable_encoder({'status': deleted, "message": "The submenu has been deleted"})
    return JSONResponse(content=json, status_code=200)

# dish


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')
def get_list_dishes(menu_id, submenu_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content=[], status_code=200)
    dishes = repo_d.get_dishes_of_submenu(submenu_id=submenu_id)
    json = jsonable_encoder(dishes)
    return JSONResponse(content=json, status_code=200)


@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def get_target_dish(menu_id, submenu_id, dish_id):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)
    dish = repo_d.get_dish(submenu_id=submenu_id, dish_id=dish_id)
    if not dish:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)
    json = jsonable_encoder(dish)
    return JSONResponse(content=json, status_code=200)


@app.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')
def post_dish(menu_id, submenu_id, title=fastapi.Body(embed=True), description=fastapi.Body(embed=True),
              price=fastapi.Body(embed=True)):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=404)
    new_dish_id = repo_d.create_dish(title=title, description=description, submenu_id=submenu_id, price=price)
    dish = repo_d.get_dish(dish_id=new_dish_id, submenu_id=submenu_id)
    json = jsonable_encoder(dish)
    return JSONResponse(content=json, status_code=201)


@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def patch_dish(menu_id, submenu_id, dish_id, title=fastapi.Body(embed=True), description=fastapi.Body(embed=True),
               price=fastapi.Body(embed=True)):
    submenu = repo_s.get_submenu(submenu_id=submenu_id, menu_id=menu_id)
    if not submenu:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)
    updated_dish_id = repo_d.update_dish(dish_id=dish_id, title=title, description=description, submenu_id=submenu_id,
                                         price=price)
    if not updated_dish_id:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)
    dish = repo_d.get_dish(dish_id=updated_dish_id, submenu_id=submenu_id)
    json = jsonable_encoder(dish)
    return JSONResponse(content=json, status_code=200)


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
    uvicorn.run(app, host="0.0.0.0", port=8000)
