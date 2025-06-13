from flask_sqlalchemy import SQLAlchemy
from .data_manager_interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        self.db = SQLAlchemy(db_file_name)

# required abstract methods
    def get_all_users(self):
        pass

    def get_user_movies(self, user_id):
        pass

    def add_user(self, user):
        pass

    def add_movie(self, movie):
        pass

    def update_movie(self, movie):
        pass

    def delete_movie(self, movie_id):
        pass