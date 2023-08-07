import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

from src.Entities.base import Base
from src.Repository import dish_repo, menu_repo, submenu_repo


class Database:

    def __init__(self) -> None:
        db_user = os.getenv('DB_USER')
        if db_user is None:
            db_user = 'postgres'
        db_password = os.getenv('DB_PASSWORD')
        if db_password is None:
            db_password = 'password'
        db_address = os.getenv('DB_ADDRESS')
        if db_address is None:
            db_address = 'localhost'
        db_name = os.getenv('DB_NAME')
        if db_name is None:
            db_name = 'mydb'

        sqlalchemy_database_url = f'postgresql://{db_user}:{db_password}@{db_address}:5432/{db_name}'
        print(sqlalchemy_database_url)
        if not database_exists(sqlalchemy_database_url):
            self.engine = create_engine(sqlalchemy_database_url)
            create_database(self.engine.url)
        else:
            self.engine = create_engine(sqlalchemy_database_url)

        Base.metadata.create_all(bind=self.engine)

        self.repo_m = menu_repo.MenuRepo(self.engine)
        self.repo_s = submenu_repo.SubmenuRepo(self.engine)
        self.repo_d = dish_repo.DishRepo(self.engine)

    def get_session(self) -> Session:
        return Session(self.engine)
