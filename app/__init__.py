
##flask dependecies importtation
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown


## Redis dependencies importation
from redis import Redis

import rq

from config import config

from config import basedir

##Firebase dependecies importation

import pyrebase
import firebase_admin
from firebase_admin import credentials

##Standard dependecies importation
import os    


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

cred = credentials.Certificate(os.path.join(basedir, 'firebase_admin_config.json'))

def create_app(config_name):

	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	#make a redis conncetion variable
	app.redis = Redis.from_url(app.config['REDIS_URL'])

	#initiate a redis Queue
	app.task_queue = rq.Queue('memy-tasks', connection=app.redis)


	#Initialize firebase User instance application

	app.firebase_user_instance = pyrebase.initialize_app(app.config['FIREBASE_CONFIG'])


	#Initialize firebase Admin instance application

	app.firebase_admin_instance = firebase_admin.initialize_app(cred, {'storageBucket':'house-of-memes.appspot.com'})


	if not app.debug and not app.testing and not app.config['SSL_DISABLE']:

		from flask_sslify import SSLify

		sslify = SSLify(app)

	bootstrap.init_app(app)
	moment.init_app(app)
	mail.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)


	from .main import main as main_blueprint
	from .auth import auth as auth_blueprint

	app.register_blueprint(main_blueprint)
	app.register_blueprint(auth_blueprint, url_prefix = '/auth')

	from .api_0_1 import api as api_blueprint
	app.register_blueprint(api_blueprint, url_prefix="/api/v1.0")

	return app