from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# User Table
class User(UserMixin, db.Model):

    __tablename__ = "MEMORYBLOG_MASTER_USER"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    firstname = db.Column(db.String(50))
    middlename = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    dob = db.Column(db.DateTime)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    photo = db.Column(db.String(20), nullable = False, default = "default_user.jpg")
    posts = db.relationship("Post", backref = "author", lazy = "dynamic")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.photo}')"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Post Table
class Post(db.Model):

    __tablename__ = "MEMORYBLOG_TRANSACTION_POST"

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    body = db.Column(db.String(150))
    created_datetime = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    updated_datetime = db.Column(db.DateTime)
    image = db.Column(db.String(20))
    video = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_MASTER_USER.id"), nullable = False)

    def __repr__(self):
        return "<Post {}>".format(self.title)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))