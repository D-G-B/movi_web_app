from ..database import db

class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    director = db.Column(db.String(60), nullable=False)
    year = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    user_id =  db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)