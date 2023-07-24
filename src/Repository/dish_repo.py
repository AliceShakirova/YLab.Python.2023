from sqlalchemy.orm import Session
from Entities.dish import Dish
from decimal import Decimal


class DishRepo:

    def __init__(self, engine):
        self.engine = engine

    def create_dish(self, title, description, price, submenu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            rounded_price = round(Decimal(price), ndigits=2)
            new_dish = Dish(title=title, description=description, price=str(rounded_price), submenu_id=submenu_id)
            db.add(new_dish)
            db.commit()
            return new_dish.id

    def get_dishes_of_submenu(self, submenu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            dishes_of_submenu = db.query(Dish).filter_by(submenu_id=submenu_id).all()
            return dishes_of_submenu

    def get_dish(self, dish_id, submenu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            dish = db.query(Dish).filter_by(id=str(dish_id), submenu_id=submenu_id).first()
            if dish:
                dish.price = str(dish.price)
            return dish

    def update_dish(self, dish_id, title, description, price, submenu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            rounded_price = round(Decimal(price), ndigits=2)
            dish_to_update = db.query(Dish).filter_by(id=str(dish_id), submenu_id=submenu_id).first()
            if dish_to_update:
                dish_to_update.title = title
                dish_to_update.description = description
                dish_to_update.price = str(rounded_price)
                db.commit()
                return dish_to_update.id
            else:
                return None

    def delete_dish(self, dish_id, submenu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            dish_to_delete = db.query(Dish).filter_by(id=str(dish_id), submenu_id=submenu_id).first()
            if not dish_to_delete:
                return False
            db.delete(dish_to_delete)
            db.commit()
            return True

    def get_dishes_of_submenus(self, ids):
        with Session(autoflush=False, bind=self.engine) as db:
            return list(db.query(Dish).filter(Dish.submenu_id.in_(ids)))