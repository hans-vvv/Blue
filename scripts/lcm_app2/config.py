import os


class Config:

    basedir = os.path.abspath(os.path.dirname(__file__))

    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '57e19ea558d4967a552d03deece34a70'

    DATABASE = 'lcm.db'
    DATABASE_PATH = os.path.join(basedir, DATABASE)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

