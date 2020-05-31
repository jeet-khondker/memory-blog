import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, render_template, flash, redirect, render_template, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_moment import Moment
from flask_mail import Mail

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = "login"
login.login_message_category = "info"

moment = Moment(app)

mail = Mail(app)

# Log Errors Via Email
if not app.debug:
    if app.config["MAIL_SERVER"]:
        auth = None
        if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
            auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        secure = None
        if app.config["MAIL_USE_TLS"]:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost = (app.config["MAIL_SERVER"], app.config["MAIL_PORT"]), 
            fromaddr = "no-reply@" + app.config["MAIL_SERVER"], 
            toaddrs = app.config["ADMINS"], 
            subject = "Memory Blog Failure", 
            credentials = auth, 
            secure = secure 
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        if not os.path.exists("logs"):
            os.mkdir("logs")
        
        file_handler = RotatingFileHandler("logs/memoryblog.log")
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("MemoryBlog StartUp")

from app import urls, models, errors

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.email == app.config["MAIL_USERNAME"]

class AdmininstrationView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.email == app.config["MAIL_USERNAME"]
    
admin = Admin(app, name = "Memory Blog Admininstration", template_mode = "bootstrap3", index_view = AdmininstrationView())

admin.add_view(AdminModelView(models.User, db.session))
admin.add_view(AdminModelView(models.Post, db.session))
admin.add_view(AdminModelView(models.Comment, db.session))
admin.add_view(AdminModelView(models.Follow, db.session))
admin.add_view(AdminModelView(models.PostLike, db.session))