from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200))


class RecipeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(5000))
    image = db.Column(db.String(5000))
    url = db.Column(db.String(5000))
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(1000))
    userid = db.Column(db.Integer)
    recipeid = db.Column(db.String(1000))


db.create_all()
