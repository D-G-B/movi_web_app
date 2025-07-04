from flask import Flask, render_template, request, redirect, url_for, flash
from database_config import db
from models import User, Movie
from data_managers import SQLiteDataManager
from validators import validate_user_data, validate_movie_data
import logging

# Initialize Flask app with instance-relative config so SQLite DB is in /instance folder
app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movi_web_app.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'check_same_thread': False}
}
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect db and initialize data manager
db.init_app(app)
data_manager = SQLiteDataManager(db)

# Create tables inside app context
with app.app_context():
    db.create_all()


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return render_template('errors/500.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(e)}")
    return render_template('errors/500.html'), 500


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/users')
def list_users():
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        flash('Error loading users. Please try again.', 'error')
        return render_template('users.html', users=[])


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    try:
        user = data_manager.get_user_by_id(user_id)
        if not user:
            flash(f'User with ID {user_id} not found.', 'error')
            return redirect(url_for('list_users'))

        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)
    except Exception as e:
        logger.error(f"Error fetching user movies for user {user_id}: {str(e)}")
        flash('Error loading user movies. Please try again.', 'error')
        return redirect(url_for('list_users'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            existing_users = data_manager.get_all_users()
            is_valid, result = validate_user_data(request.form, existing_users)

            if not is_valid:
                flash(result, 'error')
                return render_template('add_user.html')

            new_user = User(name=result['name'])
            data_manager.add_user(new_user)
            flash(f'User "{result["name"]}" added successfully!', 'success')
            return redirect(url_for('list_users'))

        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            flash('Error adding user. Please try again.', 'error')
            return render_template('add_user.html')

    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie_to_user(user_id):
    try:
        user = data_manager.get_user_by_id(user_id)
        if not user:
            flash(f'User with ID {user_id} not found.', 'error')
            return redirect(url_for('list_users'))

        if request.method == 'POST':
            existing_movies = data_manager.get_user_movies(user_id)
            is_valid, result = validate_movie_data(request.form, existing_movies)

            if not is_valid:
                flash(result, 'error')
                return render_template('add_movie.html', user=user)

            new_movie = Movie(
                name=result['name'],
                director=result['director'],
                year=result['year'],
                rating=result['rating'],
                user_id=user_id
            )
            data_manager.add_movie(new_movie)
            flash(f'Movie "{result["name"]}" added successfully!', 'success')
            return redirect(url_for('user_movies', user_id=user_id))

        return render_template('add_movie.html', user=user)

    except Exception as e:
        logger.error(f"Error in add_movie_to_user for user {user_id}: {str(e)}")
        flash('Error processing movie. Please try again.', 'error')
        return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    try:
        movie = data_manager.get_movie_by_id(movie_id)
        if not movie or movie.user_id != user_id:
            flash('Movie not found or access denied.', 'error')
            return redirect(url_for('user_movies', user_id=user_id))

        if request.method == 'POST':
            # Don't check for duplicates when updating (allow same movie to keep its values)
            is_valid, result = validate_movie_data(request.form)

            if not is_valid:
                flash(result, 'error')
                return render_template('update_movie.html', movie=movie)

            # Update movie fields
            movie.name = result['name']
            movie.director = result['director']
            movie.year = result['year']
            movie.rating = result['rating']

            data_manager.update_movie(movie)
            flash(f'Movie "{result["name"]}" updated successfully!', 'success')
            return redirect(url_for('user_movies', user_id=user_id))

        return render_template('update_movie.html', movie=movie)

    except Exception as e:
        logger.error(f"Error updating movie {movie_id} for user {user_id}: {str(e)}")
        flash('Error updating movie. Please try again.', 'error')
        return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    try:
        movie = data_manager.get_movie_by_id(movie_id)
        if not movie:
            flash('Movie not found.', 'error')
        elif movie.user_id != user_id:
            flash('Access denied.', 'error')
        else:
            movie_name = movie.name
            success = data_manager.delete_movie(movie_id)
            if success:
                flash(f'Movie "{movie_name}" deleted successfully!', 'success')
            else:
                flash('Error deleting movie.', 'error')

    except Exception as e:
        logger.error(f"Error deleting movie {movie_id} for user {user_id}: {str(e)}")
        flash('Error deleting movie. Please try again.', 'error')

    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == '__main__':
    app.run(debug=True, threaded=False)