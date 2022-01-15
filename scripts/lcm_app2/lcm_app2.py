#!/usr/bin/python3
import os
import logging
from datetime import timedelta
from flask import Flask, session
from database import database


# blueprint import
from apps.admin.views import admin
from apps.lcm.views import lcm


def setup_app(app):

    @app.before_request
    def func():
        session.modified = True


    @app.before_first_request
    def before_first_request():

        session.clear()
        app.permanent_session_lifetime = timedelta(days=1)

        app.jinja_env.filters['zip'] = zip

        log_level = logging.INFO
        for handler in app.logger.handlers:
            app.logger.removeHandler(handler)
        root = os.path.dirname(os.path.abspath(__file__))
        logdir = os.path.join(root, 'logs')
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        log_file = os.path.join(logdir, 'app.log')
        handler = logging.getLogger("LCM App")
        formatter = logging.Formatter(
        """%(asctime)s,%(levelname)s in %(module)s, [%(pathname)s:%(lineno)d]:\n%(message)s"""
        )
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)


def create_app():
    app = Flask(__name__)
    # setup with the configuration provided
    app.config.from_object('config.Config')

    # setup all our dependencies
    database.init_app(app)

    # register blueprint
    app.register_blueprint(admin)
    app.register_blueprint(lcm) 

    setup_app(app)

    return app


if __name__ == "__main__":
    create_app().run()
