from ..database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    name = db.Column(db.String(30), nullable=False)

    movies = db.relationship('Movie', backref='user', lazy=True)