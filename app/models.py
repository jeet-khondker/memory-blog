from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login

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
    comments = db.relationship("Comment", backref = "commentor", lazy = "dynamic")

    # Followers Support In User Model
    followed = db.relationship("Follow", foreign_keys = [Follow.follower_id], backref = db.backref("follower", lazy = "joined"), lazy = "dynamic", cascade = "all, delete-orphan")
    followers = db.relationship("Follow", foreign_keys = [Follow.followed_id], backref = db.backref("followed", lazy = "joined"), lazy = "dynamic", cascade = "all, delete-orphan")

    # Liked Support In User Model
    liked = db.relationship("PostLike", foreign_keys = "PostLike.user_id", backref = "user", lazy = "dynamic")

    # Commented Support In User Model
    commented = db.relationship("Comment", foreign_keys = "Comment.user_id", backref = "user", lazy = "dynamic")

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
    def get_reset_password_token(self, expires_sec = 1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    # Verifying Reset Password Token in User Model
    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id = self.id, post_id = post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id = self.id, post_id = post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id, PostLike.post_id == post.id).count() > 0

    def comment_post(self, post):
        if not self.has_commented_post(post):
            comment = Comment(user_id = self.id, post_id = post.id)
            db.session.add(comment)

    def has_commented_post(self, post):
        return Comment.query.filter(Comment.user_id == self.id, Comment.post_id == post.id).count() > 0


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

    likes = db.relationship("PostLike", backref = "post", lazy = "dynamic")

    comments = db.relationship("Comment", backref = "post", lazy = "dynamic")

    def __repr__(self):
        return f"Post('{self.title}', '{self.created_datetime}')"

# POSTS LIKE Table
class PostLike(db.Model):

    __tablename__ = "post_like"
    
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_MASTER_USER.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_TRANSACTION_POST.id"))

# COMMENTS Table
class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(2000))
    user_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_MASTER_USER.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("MEMORYBLOG_TRANSACTION_POST.id"))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"Comment('{self.user_id}', '{self.post_id}', '{self.text}', '{self.timestamp}')"








