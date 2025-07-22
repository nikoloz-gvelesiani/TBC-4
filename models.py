from flask_login import UserMixin
from ext import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10))
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img = db.Column(db.String(255))




class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __init__(self,username,password,role):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role

    def check_password(self,password):
        return check_password_hash(self.password,password)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
