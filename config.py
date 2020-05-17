import os

class Config(object):

    def get_env_var(name):
        try:
            return os.environ[name]
        except KeyError:
            message = "Expected Environment Variable '{}' Not Set!".format(name)
            raise Exception(message)

    SECRET_KEY = os.environ.get("SECRET_KEY") or "the-quick-brown-fox-jumps-over-the-lazy-dog"

    # DATABASE CONFIGURATION
    POSTGRES_URL = get_env_var("POSTGRES_URL")
    POSTGRES_USER = get_env_var("POSTGRES_USER")
    POSTGRES_PW = get_env_var("POSTGRES_PW")
    POSTGRES_DB = get_env_var("POSTGRES_DB")

    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{user}:{pw}@{url}/{db}".format(user = POSTGRES_USER, pw = POSTGRES_PW, url = POSTGRES_URL, db = POSTGRES_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # EMAIL CONFIGURATION
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    ADMINS = ["jeetzhkhondker@gmail.com"]