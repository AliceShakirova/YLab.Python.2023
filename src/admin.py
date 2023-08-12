"""from _pydecimal import Decimal

import openpyxl
from openpyxl import load_workbook
import pandas as pd

from src.Entities.dish import Dish
from src.Entities.menu import Menu
from src.Entities.submenu import Submenu

#wb: openpyxl.Workbook = load_workbook(filename='../admin/Menu.xlsx')
sheet = wb['Лист1']

#df_orders = pd.read_excel('../admin/Menu.xlsx', index_col=0, header=None)
#print(df_orders.head())

current_menu_id = None
current_submenu_id = None
list_of_menu = []
for row in wb.worksheets[0]:
    menu_id: str = row[0].value
    if menu_id is not None:
        menu_title: str = row[1].value
        menu_description: str = row[2].value
        current_menu_id = menu_id
        list_of_menu.append(Menu(menu_title, menu_description))
        continue
    submenu_id: str = row[1].value
    if submenu_id is not None:
        submenu_title: str = row[2].value
        submenu_description: str = row[3].value
        current_submenu_id = submenu_id
        list_of_menu.append(Submenu(submenu_title, submenu_description, current_menu_id))
        continue
    dish_id: str = row[2]
    if dish_id is not None:
        dish_title: str = row[3].value
        dish_description: str = row[4].value
        dish_price: Decimal = row[5].value
        list_of_menu.append(Dish(dish_title, dish_description, current_submenu_id, dish_price))

for inst in list_of_menu:
    print(inst.title, ':', inst.description)
"""
