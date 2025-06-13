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

if __name__ == '__main__':
    app.run(debug=True)