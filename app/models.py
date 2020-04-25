from app import app, db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt

# FOLLOW Association Table
class Follow(db.Model):

    __tablename__ = "MEMORYBLOG_ASSOCIATION_FOLLOW"

    follower_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_MASTER_USER.id"), primary_key = True)
    followed_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_MASTER_USER.id"), primary_key = True)
    follow_time = db.Column(db.DateTime, default = datetime.utcnow)

# USER Table
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
    last_seen = db.Column(db.DateTime, default = datetime.utcnow)
    posts = db.relationship("Post", backref = "author", lazy = "dynamic")

    # Followers Support in User Model
    followed = db.relationship("Follow", foreign_keys = [Follow.follower_id], backref = db.backref("follower", lazy = "joined"), lazy = "dynamic", cascade = "all, delete-orphan")
    followers = db.relationship("Follow", foreign_keys = [Follow.followed_id], backref = db.backref("followed", lazy = "joined"), lazy = "dynamic", cascade = "all, delete-orphan")

    # Private Messages Support in User Model
    messages_sent = db.relationship("Message", foreign_keys = "Message.sender_id", backref = "author", lazy = "dynamic")
    messages_received = db.relationship("Message", foreign_keys = "Message.recipient_id", backref = "recipient", lazy = "dynamic")
    last_message_seen_time = db.Column(db.DateTime)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.photo}')"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Followers Support in User Model
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower = self, followed = user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id = user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id = user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id = user.id).first() is not None

    # Reset Password Support in User Model
    def get_reset_password_token(self, expires_in = 600):
        return jwt.encode({
            "reset_password": self.id, "expire": time() + expires_in
        }, app.config["SECRET_KEY"], algorithm = "HS256").decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms = ["HS256"])["reset_password"]
        except:
            return
        return User.query.get(id)

    # Private Messages Support in User Model
    def new_messages(self):
        last_seen_time = self.last_message_seen_time or datetime(1900, 1, 1) # Default: 1st January 1900 if not available
        return Message.query.filter_by(recipients = self).filter(Message.delivered_time > last_seen_time).count()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# POST Table
class Post(db.Model):

    __tablename__ = "MEMORYBLOG_TRANSACTION_POST"

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    body = db.Column(db.String(1000))
    created_datetime = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    updated_datetime = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_MASTER_USER.id"), nullable = False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.created_datetime}')"

# Message Model
class Message(db.Model):
    
    __tablename__ = "MEMORYBLOG_TRANSACTION_USER_MESSAGE"

    id = db.Column(db.Integer, primary_key = True)
    sender_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_MASTER_USER.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_MASTER_USER.id"))
    body = db.Column(db.String(1000))
    delivered_time = db.Column(db.DateTime, index = True, default = datetime.utcnow)

    def __repr__(self):
        return f"Message('{self.body}')"






