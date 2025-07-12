from .data_manager_interface import DataManagerInterface
from models import User, Movie
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db):
        self.db = db

    def _safe_query(self, query_func, error_message):
        """Helper to execute database read queries with generic error handling and logging."""
        try:
            return query_func()
        except SQLAlchemyError as e:
            logger.error(f"{error_message}: {str(e)}")
            self.db.session.rollback() # Rollback in case of database error
            raise
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            raise

    def _safe_transaction(self, transaction_func, success_message, error_message_base, integrity_error_message=None):
        """
        Helper to execute database write operations (add, update, delete) with generic error handling,
        commit, and rollback.
        """
        try:
            result = transaction_func()
            self.db.session.commit()
            logger.info(success_message)
            return result
        except IntegrityError as e:
            self.db.session.rollback()
            logger.error(f"Integrity error in {error_message_base}: {str(e)}")
            # Provide a specific message if available, otherwise a generic one
            raise ValueError(integrity_error_message or f"A duplicate entry or related integrity issue occurred during {error_message_base}.")
        except SQLAlchemyError as e:
            self.db.session.rollback()
            logger.error(f"Database error in {error_message_base}: {str(e)}")
            raise
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Unexpected error in {error_message_base}: {str(e)}")
            raise

    def get_all_users(self):
        """Get all users from the database"""
        return self._safe_query(lambda: User.query.all(), "Error fetching all users")

    def get_user_movies(self, user_id):
        """Get all movies for a specific user"""
        return self._safe_query(lambda: Movie.query.filter_by(user_id=user_id).all(),
                                "Error fetching movies for user")

    def add_user(self, user):
        """Add a new user to the database"""
        if not user or not hasattr(user, 'name'):
            raise ValueError("Invalid user object for addition.")

        def _add_user_op():
            self.db.session.add(user)
            return user

        return self._safe_transaction(
            _add_user_op,
            f"User '{user.name}' added successfully",
            "adding user",
            "A user with this name already exists."
        )

    def add_movie(self, movie):
        """Add a new movie to the database"""
        if not movie or not hasattr(movie, 'name') or not hasattr(movie, 'director'):
            raise ValueError("Invalid movie object for addition.")
        if not movie.user_id:
            raise ValueError("Movie must be associated with a user")

        # Database-specific validation: Check if user exists (referential integrity)
        user = self.get_user_by_id(movie.user_id)
        if not user:
            raise ValueError(f"User with ID {movie.user_id} does not exist")

        def _add_movie_op():
            self.db.session.add(movie)
            return movie

        return self._safe_transaction(
            _add_movie_op,
            f"Movie '{movie.name}' added for user {movie.user_id}",
            "adding movie",
            "This movie already exists in your collection for this user."
        )

    def delete_movie(self, movie_id):
        """Delete a movie from the database"""
        if not movie_id:
            raise ValueError("Movie ID is required")

        movie = self._safe_query(lambda: Movie.query.get(movie_id),
                                 "Error retrieving movie for deletion")
        if not movie:
            logger.warning(f"Attempted to delete non-existent movie with ID {movie_id}")
            return False # Indicate that no movie was found to delete

        movie_name = movie.name # Store name before deletion for logging/return

        def _delete_movie_op():
            self.db.session.delete(movie)
            return True # Indicate successful deletion operation for the helper

        return self._safe_transaction(
            _delete_movie_op,
            f"Movie '{movie_name}' (ID: {movie_id}) deleted successfully",
            "deleting movie"
        )


    def update_movie(self, movie):
        """Update an existing movie in the database"""
        if not movie or not hasattr(movie, 'id'):
            raise ValueError("Invalid movie object for update")

        # Get existing movie to ensure it's tracked by session and for initial existence check
        existing_movie = self.get_movie_by_id(movie.id)
        if not existing_movie:
            raise ValueError(f"Movie with ID {movie.id} does not exist for update")

        # Update the existing_movie object with new values from the passed 'movie' object
        # Assuming movie object comes pre-populated with new values from service layer
        existing_movie.name = movie.name
        existing_movie.director = movie.director
        existing_movie.year = movie.year
        existing_movie.rating = movie.rating

        def _update_movie_op():
            return existing_movie

        return self._safe_transaction(
            _update_movie_op,
            f"Movie '{existing_movie.name}' (ID: {existing_movie.id}) updated successfully",
            "updating movie",
            "A movie with this name and director already exists for this user."
        )

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

    # These two methods not currently in use,  might be used later
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