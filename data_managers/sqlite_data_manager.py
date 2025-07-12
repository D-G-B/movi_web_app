from .data_manager_interface import DataManagerInterface
from models import User, Movie
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db):
        self.db = db

    def _safe_query(self, query_func, error_message, *args, **kwargs):
        """Helper to execute database queries with generic error handling and logging.
           If query_func is a lambda capturing its own args, *args and **kwargs should be empty.
        """
        try:
            # Execute the query function, passing args/kwargs only if it expects them.
            # For lambdas that capture args (like `lambda: User.query.get(user_id)`),
            # args and kwargs should be empty when calling _safe_query.
            return query_func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"{error_message}: {str(e)}")
            self.db.session.rollback() # Rollback in case of database error
            raise # Re-raise to be handled by service layer or app error handler
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            raise

    def get_all_users(self):
        """Get all users from the database"""
        return self._safe_query(User.query.all, "Error fetching all users")

    def get_user_movies(self, user_id):
        """Get all movies for a specific user"""
        return self._safe_query(lambda: Movie.query.filter_by(user_id=user_id).all(),
                                "Error fetching movies for user")

    def add_user(self, user):
        """Add a new user to the database"""
        # Specific validation that can lead to IntegrityError or ValueErrors
        if not user or not hasattr(user, 'name'):
            raise ValueError("Invalid user object")
        if not user.name or not user.name.strip():
            raise ValueError("User name cannot be empty")

        try:
            self.db.session.add(user)
            self.db.session.commit()
            logger.info(f"User '{user.name}' added successfully")
            return user
        except IntegrityError as e:
            self.db.session.rollback()
            logger.error(f"Integrity error adding user: {str(e)}")
            raise ValueError("A user with this name already exists.")
        except SQLAlchemyError as e:
            self.db.session.rollback()
            logger.error(f"Database error adding user: {str(e)}")
            raise
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Unexpected error adding user: {str(e)}")
            raise

    def add_movie(self, movie):
        """Add a new movie to the database"""
        # Specific validation
        if not movie or not hasattr(movie, 'name') or not hasattr(movie, 'director'):
            raise ValueError("Invalid movie object")
        if not movie.name or not movie.name.strip():
            raise ValueError("Movie name cannot be empty")
        if not movie.director or not movie.director.strip():
            raise ValueError("Movie director cannot be empty")
        if not movie.user_id:
            raise ValueError("Movie must be associated with a user")

        user = self.get_user_by_id(movie.user_id)
        if not user:
            raise ValueError(f"User with ID {movie.user_id} does not exist")

        try:
            self.db.session.add(movie)
            self.db.session.commit()
            logger.info(f"Movie '{movie.name}' added for user {movie.user_id}")
            return movie
        except IntegrityError as e:
            self.db.session.rollback()
            logger.error(f"Integrity error adding movie: {str(e)}")
            raise ValueError("This movie already exists in your collection for this user.")
        except SQLAlchemyError as e:
            self.db.session.rollback()
            logger.error(f"Database error adding movie: {str(e)}")
            raise
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Unexpected error adding movie: {str(e)}")
            raise

    def delete_movie(self, movie_id):
        """Delete a movie from the database"""
        if not movie_id:
            raise ValueError("Movie ID is required")

        movie = self._safe_query(lambda: Movie.query.get(movie_id),
                                 "Error retrieving movie for deletion")
        if not movie:
            logger.warning(f"Attempted to delete non-existent movie with ID {movie_id}")
            return False

        movie_name = movie.name
        try:
            self.db.session.delete(movie)
            self.db.session.commit()
            logger.info(f"Movie '{movie_name}' (ID: {movie_id}) deleted successfully")
            return True
        except SQLAlchemyError as e:
            self.db.session.rollback()
            logger.error(f"Database error deleting movie {movie_id}: {str(e)}")
            raise
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Unexpected error deleting movie {movie_id}: {str(e)}")
            raise

    def update_movie(self, movie):
        """Update an existing movie in the database"""
        if not movie or not hasattr(movie, 'id'):
            raise ValueError("Invalid movie object for update")

        # Get existing movie to ensure it's tracked by session (or simply re-fetch it)
        existing_movie = self.get_movie_by_id(movie.id)
        if not existing_movie:
            raise ValueError(f"Movie with ID {movie.id} does not exist for update")

        # Update the existing_movie object with new values from the passed 'movie' object
        existing_movie.name = movie.name
        existing_movie.director = movie.director
        existing_movie.year = movie.year
        existing_movie.rating = movie.rating

        # Specific field validations
        if not existing_movie.name or not existing_movie.name.strip():
            raise ValueError("Movie name cannot be empty")
        if not existing_movie.director or not existing_movie.director.strip():
            raise ValueError("Director name cannot be empty")
        if existing_movie.rating is not None and (existing_movie.rating < 1 or existing_movie.rating > 10):
            raise ValueError("Rating must be between 1 and 10")
        if existing_movie.year is not None and (existing_movie.year < 1900 or existing_movie.year > 2025):
            raise ValueError("Year must be between 1900 and 2025")

        try:
            self.db.session.commit()
            logger.info(f"Movie '{existing_movie.name}' (ID: {existing_movie.id}) updated successfully")
            return existing_movie
        except IntegrityError as e:
            self.db.session.rollback()
            logger.error(f"Integrity error updating movie: {str(e)}")
            raise ValueError("A movie with this name and director already exists for this user.")
        except SQLAlchemyError as e:
            self.db.session.rollback()
            logger.error(f"Database error updating movie: {str(e)}")
            raise
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Unexpected error updating movie: {str(e)}")
            raise

    def get_movie_by_id(self, movie_id):
        """Get a specific movie by its ID"""
        if not movie_id:
            raise ValueError("Movie ID is required")
        return self._safe_query(lambda: Movie.query.get(movie_id),
                                "Error fetching movie by ID")

    def get_user_by_id(self, user_id):
        """Get a specific user by their ID"""
        if not user_id:
            raise ValueError("User ID is required")
        return self._safe_query(lambda: User.query.get(user_id),
                                "Error fetching user by ID")

     # Both functions below not used yet, will maybe implement later
    def get_user_movie_count(self, user_id):
        """Get the count of movies for a specific user"""
        if not user_id:
            raise ValueError("User ID is required")
        return self._safe_query(lambda: Movie.query.filter_by(user_id=user_id).count(),
                                "Error counting movies for user")

    def search_movies(self, user_id, search_term):
        """Search movies for a user by name or director"""
        if not user_id:
            raise ValueError("User ID is required")

        if not search_term or not search_term.strip():
            return self.get_user_movies(user_id)

        search_term_pattern = f"%{search_term.strip()}%"
        return self._safe_query(lambda: Movie.query.filter_by(user_id=user_id).filter(
            (Movie.name.ilike(search_term_pattern)) |
            (Movie.director.ilike(search_term_pattern))
        ).all(), "Error searching movies for user")