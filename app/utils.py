import pyrebase
from flask import current_app


def firebase_app_initiate():

	return pyrebase.initialize_app(current_app.config['FIREBASE_CONFIG'])


