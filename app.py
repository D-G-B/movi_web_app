from flask import Flask
from database_config import db
from models import User, Movie

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movi_web_app.db'

# Connect db to app
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Hello World!"

@app.route('/users')
def list_users():
    pass

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