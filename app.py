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

@app.route('/users/<user_id>')
def users_movies():
    pass

@app.route('/add_user')
def add_user():
    pass

@app.route('/users/<user_id>/add_movie')
def add_movie_to_user():
    pass

@app.route('/users/<user_id>/update_movie/<movie_id>')
def update_movie():
    pass

@app.route('/users/<user_id>/delete_movie/<movie_id>')
def delete_movie():
    pass

if __name__ == '__main__':
    app.run(debug=True)