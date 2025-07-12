"""
Service layer for MovieWeb App
Handles business logic and data operations
"""
import logging
from validators import validate_user_data, validate_movie_data
from models import User, Movie

logger = logging.getLogger(__name__)


class BaseService:
    """Base class for services to handle common patterns like error wrapping."""
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def _execute_service_method(self, func, *args, **kwargs):
        """Helper method to wrap service calls with generic error handling."""
        try:
            return True, func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Service validation error: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected service error in {func.__name__}: {str(e)}")
            return False, "An unexpected error occurred. Please try again."


class UserService(BaseService):
    def get_all_users(self):
        """Get all users with error handling"""
        # DataManager already logs specific DB errors, just re-raise if needed
        return self.data_manager.get_all_users()

    def get_user_by_id(self, user_id):
        """Get a user by ID with error handling"""
        return self.data_manager.get_user_by_id(user_id)

    def create_user(self, form_data):
        """
        Create a new user with validation

        Returns:
            tuple: (success, user_or_error_message)
        """
        existing_users = self.data_manager.get_all_users()
        is_valid, result = validate_user_data(form_data, existing_users)
        if not is_valid:
            return False, result

        def _add_user_operation():
            new_user = User(name=result['name'])
            return self.data_manager.add_user(new_user)

        return self._execute_service_method(_add_user_operation)


class MovieService(BaseService):
    def get_user_movies(self, user_id):
        """Get movies for a user with error handling"""
        return self.data_manager.get_user_movies(user_id)

    def get_movie_by_id(self, movie_id):
        """Get a movie by ID with error handling"""
        return self.data_manager.get_movie_by_id(movie_id)

    def create_movie(self, user_id, form_data):
        """
        Create a new movie with validation

        Returns:
            tuple: (success, movie_or_error_message)
        """
        existing_movies = self.data_manager.get_user_movies(user_id)
        is_valid, result = validate_movie_data(form_data, existing_movies)
        if not is_valid:
            return False, result

        def _add_movie_operation():
            new_movie = Movie(
                name=result['name'],
                director=result['director'],
                year=result['year'],
                rating=result['rating'],
                user_id=user_id
            )
            return self.data_manager.add_movie(new_movie)

        return self._execute_service_method(_add_movie_operation)

    def update_movie(self, movie_id, form_data):
        """
        Update an existing movie with validation

        Returns:
            tuple: (success, movie_or_error_message)
        """
        movie = self.data_manager.get_movie_by_id(movie_id)
        if not movie:
            return False, "Movie not found."

        # For update, we validate data against general rules, not against existing duplicates
        is_valid, result = validate_movie_data(form_data)
        if not is_valid:
            return False, result

        def _update_movie_operation():
            movie.name = result['name']
            movie.director = result['director']
            movie.year = result['year']
            movie.rating = result['rating']
            return self.data_manager.update_movie(movie)

        return self._execute_service_method(_update_movie_operation)

    def delete_movie(self, movie_id):
        """
        Delete a movie

        Returns:
            tuple: (success, movie_name_or_error_message)
        """
        movie = self.data_manager.get_movie_by_id(movie_id)
        if not movie:
            return False, "Movie not found."

        movie_name = movie.name

        def _delete_movie_operation():
            success = self.data_manager.delete_movie(movie_id)
            if success:
                return movie_name
            else:
                # If data_manager.delete_movie returns False, it implies an issue already logged
                raise ValueError("Error deleting movie.")

        return self._execute_service_method(_delete_movie_operation)

    def validate_movie_ownership(self, movie_id, user_id):
        """
        Check if a movie belongs to a specific user

        Returns:
            tuple: (is_valid, movie_or_error_message)
        """
        try:
            movie = self.data_manager.get_movie_by_id(movie_id)
            if not movie:
                return False, "Movie not found."

            if movie.user_id != user_id:
                return False, "Access denied."

            return True, movie

        except Exception as e:
            logger.error(f"Error validating movie ownership: {str(e)}")
            return False, "Error validating movie access."