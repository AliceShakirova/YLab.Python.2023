from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database

from src.Entities.base import Base
from src.Repository import menu_repo, dish_repo, submenu_repo


class Database:

    def __init__(self, user, password, host, port, db_name):
        sqlalchemy_database_url = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'

        if not database_exists(sqlalchemy_database_url):
            self.engine = create_engine(sqlalchemy_database_url)
            create_database(self.engine.url)
        else:
            self.engine = create_engine(sqlalchemy_database_url)

        Base.metadata.create_all(bind=self.engine)

        self.repo_m = menu_repo.MenuRepo(self.engine)
        self.repo_s = submenu_repo.SubmenuRepo(self.engine)
        self.repo_d = dish_repo.DishRepo(self.engine)

    def get_session(self):
        return Session(self.engine)


