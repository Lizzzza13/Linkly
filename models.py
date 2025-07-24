from flask_login import UserMixin
from ext import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String, nullable=True)
    short_url = db.Column(db.String, unique=True, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref='urls')


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    img = db.Column(db.String(), default="default.png")
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), default="Guest")

    def __init__(self, username, email, password, role="Guest", img="default.png"):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role
        self.img = img

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
