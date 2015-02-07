import os
from flask.ext.login import LoginManager
from flask.ext.openid import openid
from config import basedir

loginmanager = LoginManager()
loginmanager.init_app(app)
openid = OpenID(app, os.path.join(basedir, 'tmp'))