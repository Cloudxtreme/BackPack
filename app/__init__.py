from flask import Flask, Response
from config import config
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'home'


def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  db.init_app(app)
  login_manager.init_app(app)
  #app factory function for configuration
  #Use blueprints since nonglobal apps can't route
  #Leave at bottom to avoid conflicts
  from .backpack import backpack as backpack_blueprint
  app.register_blueprint(backpack_blueprint)

  return app