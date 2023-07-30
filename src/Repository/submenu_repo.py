from sqlalchemy.orm import Session
from src.Entities.submenu import Submenu


class SubmenuRepo:

    def __init__(self, engine):
        self.engine = engine

    def create_submenu(self, title, description, menu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            new_submenu = Submenu(title=title, description=description, menu_id=menu_id)
            db.add(new_submenu)
            db.commit()
            db.refresh(new_submenu)
            return new_submenu

    def get_all_submenus(self):
        with Session(autoflush=False, bind=self.engine) as db:
            all_submenus = db.query(Submenu).all()
            return all_submenus

    def get_submenu(self, menu_id, submenu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            return db.query(Submenu).filter_by(id=str(submenu_id), menu_id=menu_id).first()

    def update_submenu(self, submenu_id, title, description, menu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            submenu_to_update = db.query(Submenu).filter_by(id=str(submenu_id), menu_id=menu_id).first()
            if submenu_to_update:
                submenu_to_update.title = title
                submenu_to_update.description = description
                db.commit()
                db.refresh(submenu_to_update)
                return submenu_to_update

    def delete_submenu(self, submenu_id, menu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            submenu_to_delete = db.query(Submenu).filter_by(id=str(submenu_id), menu_id=menu_id).first()
            if not submenu_to_delete:
                return False
            db.delete(submenu_to_delete)
            db.commit()
            return True

    def get_submenus_of_menu(self, menu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            return db.query(Submenu).filter_by(menu_id=str(menu_id)).all()

    def get_submenus_count(self, menu_id):
        with Session(autoflush=False, bind=self.engine) as db:
            return db.query(Submenu).filter_by(menu_id=str(menu_id)).count()
