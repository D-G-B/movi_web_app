from flask import Flask, render_template, request, redirect, url_for
from database_config import db
from models import User, Movie
from data_managers import SQLiteDataManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movi_web_app.db'

# Connect db to app
db.init_app(app)

# Initialize data manager
data_manager = SQLiteDataManager(db)

# Create tables
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return "Hello World!"


@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return "User not found", 404
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        new_user = User(name=name)
        data_manager.add_user(new_user)
        return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie_to_user(user_id):
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        name = request.form['name']
        director = request.form['director']
        year = int(request.form['year']) if request.form['year'] else None
        rating = int(request.form['rating']) if request.form['rating'] else None

        new_movie = Movie(
            name=name,
            director=director,
            year=year,
            rating=rating,
            user_id=user_id
        )
        data_manager.add_movie(new_movie)
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    movie = data_manager.get_movie_by_id(movie_id)
    if not movie or movie.user_id != user_id:
        return "Movie not found", 404

    if request.method == 'POST':
        movie.name = request.form['name']
        movie.director = request.form['director']
        movie.year = int(request.form['year']) if request.form['year'] else None
        movie.rating = int(request.form['rating']) if request.form['rating'] else None

        data_manager.update_movie(movie)
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    movie = data_manager.get_movie_by_id(movie_id)
    if movie and movie.user_id == user_id:
        data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == '__main__':
    app.run(debug=True)