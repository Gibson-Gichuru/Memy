import pyrebase
from flask import current_app

from firebase_admin import auth as admin_auth

from flask import current_app

from threading import Thread

def generate_firebase_login_token(user_unique_token):

	return admin_auth.create_custom_token(user_unique_token)


def firebase_login(user_unique_token):

	login_token = generate_firebase_login_token(user_unique_token)

	app = app = current_app._get_current_object()

	firebase_login_thread = Thread(target=async_login_to_firebase, args=[login_token, app])

	firebase_login_thread.start()

	return firebase_login_thread 

def async_login_to_firebase(login_token, app):

	with app.app_context():

		try:
			user_auth = current_app.config["FIREBASE_USER_APP_INSTANCE"].auth()

			return user_auth.sign_in_with_custom_token(login_token.decode('utf-8'))

		except:

			pass


