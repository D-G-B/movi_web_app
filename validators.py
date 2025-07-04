"""
Input validation functions for the Movie Web App
"""


def validate_user_name(name, existing_users=None):
    """
    Validate username input

    Args:
        name: The username to validate
        existing_users: List of existing users to check for duplicates

    Returns:
        tuple: (is_valid, error_message)
    """
    if not name:
        return False, "User name is required."

    if len(name) > 30:
        return False, "User name must be 30 characters or less."

    if existing_users:
        if any(user.name.lower() == name.lower() for user in existing_users):
            return False, "A user with this name already exists."

    return True, None


def validate_movie_name(name):
    """
    Validate movie name input

    Args:
        name: The movie name to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not name:
        return False, "Movie name is required."

    if len(name) > 60:
        return False, "Movie name must be 60 characters or less."

    return True, None


def validate_director_name(director):
    """
    Validate director name input

    Args:
        director: The director name to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not director:
        return False, "Director name is required."

    if len(director) > 60:
        return False, "Director name must be 60 characters or less."

    return True, None


def validate_year(year_str):
    """
    Validate and convert year input

    Args:
        year_str: The year string to validate

    Returns:
        tuple: (is_valid, year_int_or_error_message)
    """
    if not year_str:
        return True, None  # Year is optional

    try:
        year = int(year_str)
        if year < 1900 or year > 2025:
            return False, "Year must be between 1900 and 2025."
        return True, year
    except ValueError:
        return False, "Please enter a valid year."


def validate_rating(rating_str):
    """
    Validate and convert rating input

    Args:
        rating_str: The rating string to validate

    Returns:
        tuple: (is_valid, rating_int_or_error_message)
    """
    if not rating_str:
        return True, None  # Rating is optional

    try:
        rating = int(rating_str)
        if rating < 1 or rating > 10:
            return False, "Rating must be between 1 and 10."
        return True, rating
    except ValueError:
        return False, "Please enter a valid rating."


def validate_movie_duplicate(name, director, existing_movies):
    """
    Check if a movie already exists in the user's collection

    Args:
        name: Movie name
        director: Director name
        existing_movies: List of existing movies for the user

    Returns:
        tuple: (is_unique, error_message)
    """
    if any(movie.name.lower() == name.lower() and movie.director.lower() == director.lower()
           for movie in existing_movies):
        return False, "This movie already exists in your collection."

    return True, None


def validate_movie_data(form_data, existing_movies=None):
    """
    Validate all movie form data at once

    Args:
        form_data: Dictionary containing form data
        existing_movies: List of existing movies (for duplicate check)

    Returns:
        tuple: (is_valid, validated_data_or_error_message)
    """
    name = form_data.get('name', '').strip()
    director = form_data.get('director', '').strip()
    year_str = form_data.get('year', '').strip()
    rating_str = form_data.get('rating', '').strip()

    # Validate movie name
    is_valid, error = validate_movie_name(name)
    if not is_valid:
        return False, error

    # Validate director name
    is_valid, error = validate_director_name(director)
    if not is_valid:
        return False, error

    # Validate year
    is_valid, year_or_error = validate_year(year_str)
    if not is_valid:
        return False, year_or_error
    year = year_or_error

    # Validate rating
    is_valid, rating_or_error = validate_rating(rating_str)
    if not is_valid:
        return False, rating_or_error
    rating = rating_or_error

    # Check for duplicates if existing_movies provided
    if existing_movies is not None:
        is_unique, error = validate_movie_duplicate(name, director, existing_movies)
        if not is_unique:
            return False, error

    # Return validated data
    return True, {
        'name': name,
        'director': director,
        'year': year,
        'rating': rating
    }


def validate_user_data(form_data, existing_users=None):
    """
    Validate all user form data at once

    Args:
        form_data: Dictionary containing form data
        existing_users: List of existing users (for duplicate check)

    Returns:
        tuple: (is_valid, validated_data_or_error_message)
    """
    name = form_data.get('name', '').strip()

    is_valid, error = validate_user_name(name, existing_users)
    if not is_valid:
        return False, error

    return True, {'name': name}