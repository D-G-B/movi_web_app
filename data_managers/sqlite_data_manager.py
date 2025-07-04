from .data_manager_interface import DataManagerInterface
from models import User, Movie
import logging

logger = logging.getLogger(__name__)


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db):
        self.db = db

    def get_all_users(self):
        """Get all users from the database"""
        try:
            return User.query.all()
        except Exception as e:
            logger.error(f"Error fetching all users: {str(e)}")
            raise

    def get_user_movies(self, user_id):
        """Get all movies for a specific user"""
        try:
            return Movie.query.filter_by(user_id=user_id).all()
        except Exception as e:
            logger.error(f"Error fetching movies for user {user_id}: {str(e)}")
            raise

    def add_user(self, user):
        """Add a new user to the database"""
        try:
            # Validate user object
            if not user or not hasattr(user, 'name'):
                raise ValueError("Invalid user object")

            if not user.name or not user.name.strip():
                raise ValueError("User name cannot be empty")

            self.db.session.add(user)
            self.db.session.commit()
            logger.info(f"User '{user.name}' added successfully")
            return user
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error adding user: {str(e)}")
            raise

    def add_movie(self, movie):
        """Add a new movie to the database"""
        try:
            # Validate movie object
            if not movie or not hasattr(movie, 'name') or not hasattr(movie, 'director'):
                raise ValueError("Invalid movie object")

            if not movie.name or not movie.name.strip():
                raise ValueError("Movie name cannot be empty")

            if not movie.director or not movie.director.strip():
                raise ValueError("Movie director cannot be empty")

            if not movie.user_id:
                raise ValueError("Movie must be associated with a user")

            # Validate user exists
            user = User.query.get(movie.user_id)
            if not user:
                raise ValueError(f"User with ID {movie.user_id} does not exist")

            self.db.session.add(movie)
            self.db.session.commit()
            logger.info(f"Movie '{movie.name}' added for user {movie.user_id}")
            return movie
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error adding movie: {str(e)}")
            raise

    def delete_movie(self, movie_id):
        """Delete a movie from the database"""
        try:
            if not movie_id:
                raise ValueError("Movie ID is required")

            movie = Movie.query.get(movie_id)
            if not movie:
                logger.warning(f"Attempted to delete non-existent movie with ID {movie_id}")
                return False

            movie_name = movie.name
            self.db.session.delete(movie)
            self.db.session.commit()
            logger.info(f"Movie '{movie_name}' (ID: {movie_id}) deleted successfully")
            return True
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting movie {movie_id}: {str(e)}")
            raise

    def update_movie(self, movie):
        """Update an existing movie in the database"""
        try:
            if not movie or not hasattr(movie, 'id'):
                raise ValueError("Invalid movie object")

            # Validate movie exists in database
            existing_movie = Movie.query.get(movie.id)
            if not existing_movie:
                raise ValueError(f"Movie with ID {movie.id} does not exist")

            # Validate required fields
            if not movie.name or not movie.name.strip():
                raise ValueError("Movie name cannot be empty")

            if not movie.director or not movie.director.strip():
                raise ValueError("Movie director cannot be empty")

            # Validate rating if provided
            if movie.rating is not None and (movie.rating < 1 or movie.rating > 10):
                raise ValueError("Rating must be between 1 and 10")

            # Validate year if provided
            if movie.year is not None and (movie.year < 1900 or movie.year > 2025):
                raise ValueError("Year must be between 1900 and 2025")

            self.db.session.commit()
            logger.info(f"Movie '{movie.name}' (ID: {movie.id}) updated successfully")
            return movie
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating movie: {str(e)}")
            raise

    def get_movie_by_id(self, movie_id):
        """Get a specific movie by its ID"""
        try:
            if not movie_id:
                raise ValueError("Movie ID is required")

            return Movie.query.get(movie_id)
        except Exception as e:
            logger.error(f"Error fetching movie {movie_id}: {str(e)}")
            raise

    def get_user_by_id(self, user_id):
        """Get a specific user by their ID"""
        try:
            if not user_id:
                raise ValueError("User ID is required")

            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            raise

    def get_user_movie_count(self, user_id):
        """Get the count of movies for a specific user"""
        try:
            if not user_id:
                raise ValueError("User ID is required")

            return Movie.query.filter_by(user_id=user_id).count()
        except Exception as e:
            logger.error(f"Error counting movies for user {user_id}: {str(e)}")
            raise

    def search_movies(self, user_id, search_term):
        """Search movies for a user by name or director"""
        try:
            if not user_id:
                raise ValueError("User ID is required")

            if not search_term or not search_term.strip():
                return self.get_user_movies(user_id)

            search_term = f"%{search_term.strip()}%"
            return Movie.query.filter_by(user_id=user_id).filter(
                (Movie.name.ilike(search_term)) |
                (Movie.director.ilike(search_term))
            ).all()
        except Exception as e:
            logger.error(f"Error searching movies for user {user_id}: {str(e)}")
            raise