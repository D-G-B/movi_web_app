from flask import Flask, render_template, request, redirect, url_for, flash
from database_config import db
from data_managers import SQLiteDataManager
from services import UserService, MovieService
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

# Connect db and initialize data manager and services
db.init_app(app)
data_manager = SQLiteDataManager(db)
user_service = UserService(data_manager)
movie_service = MovieService(data_manager)

# Create tables inside app context
with app.app_context():
    db.create_all()


# Helper to handle service responses
def handle_service_response(success, result, success_message, redirect_url, template_name=None, **kwargs):
    if success:
        flash(success_message, 'success')
        return redirect(redirect_url)
    else:
        flash(result, 'error') # result contains the error message
        if template_name:
            return render_template(template_name, **kwargs)
        else:
            return redirect(redirect_url) # Fallback redirect if no template provided

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
    # Log the full traceback for unhandled exceptions
    import traceback
    logger.error(traceback.format_exc())
    return render_template('errors/500.html'), 500


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/users')
def list_users():
    try:
        users = user_service.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        flash('Error loading users. Please try again.', 'error')
        return render_template('users.html', users=[])


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        flash(f'User with ID {user_id} not found.', 'error')
        return redirect(url_for('list_users'))

    try:
        movies = movie_service.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)
    except Exception as e:
        flash('Error loading user movies. Please try again.', 'error')
        return redirect(url_for('list_users'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        success, result = user_service.create_user(request.form)
        return handle_service_response(
            success, result,
            f'User "{result.name}" added successfully!' if success else None,
            url_for('list_users'),
            template_name='add_user.html'
        )
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie_to_user(user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        flash(f'User with ID {user_id} not found.', 'error')
        return redirect(url_for('list_users'))

    if request.method == 'POST':
        success, result = movie_service.create_movie(user_id, request.form)
        return handle_service_response(
            success, result,
            f'Movie "{result.name}" added successfully!' if success else None,
            url_for('user_movies', user_id=user_id),
            template_name='add_movie.html', user=user
        )
    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    is_valid, movie = movie_service.validate_movie_ownership(movie_id, user_id)
    if not is_valid:
        flash(movie, 'error')  # movie contains error message
        return redirect(url_for('user_movies', user_id=user_id))

    if request.method == 'POST':
        success, result = movie_service.update_movie(movie_id, request.form)
        return handle_service_response(
            success, result,
            f'Movie "{result.name}" updated successfully!' if success else None,
            url_for('user_movies', user_id=user_id),
            template_name='update_movie.html', movie=movie # Re-render with current movie if error
        )
    return render_template('update_movie.html', movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    is_valid, movie = movie_service.validate_movie_ownership(movie_id, user_id)
    if not is_valid:
        flash(movie, 'error')  # movie contains error message
        return redirect(url_for('user_movies', user_id=user_id))

    success, result = movie_service.delete_movie(movie_id)
    return handle_service_response(
        success, result,
        f'Movie "{result}" deleted successfully!' if success else None,
        url_for('user_movies', user_id=user_id)
    )


if __name__ == '__main__':
    app.run(debug=True, threaded=False)