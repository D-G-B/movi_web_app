from .data_manager_interface import DataManagerInterface
from models import User, Movie

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db):
        self.db = db

# required abstract methods
    def get_all_users(self):
        """Get all users from the database"""
        return User.query.all()

    def get_user_movies(self, user_id):
        """Get all movies for a specific user"""
        return Movie.query.filter_by(user_id=user_id).all()

    def add_user(self, user):
        """Add a new user to the database"""
        try:
            self.db.session.add(user)
            self.db.session.commit()
            return user
        except Exception as e:
            self.db.session.rollback()
            raise e

    def add_movie(self, movie):
        """Add a new movie to the database"""
        try:
            self.db.session.add(movie)
            self.db.session.commit()
            return movie
        except Exception as e:
            self.db.session.rollback()
            raise e

    def delete_movie(self, movie_id):
        """Delete a movie from the database"""
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                self.db.session.delete(movie)
                self.db.session.commit()
                return True
            return False
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_movie_by_id(self, movie_id):
        """Get a specific movie by its ID"""
        return Movie.query.get(movie_id)

    def get_user_by_id(self, user_id):
        """Get a specific user by their ID"""
        return User.query.get(user_id)