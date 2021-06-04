import pyrebase
from flask import current_app

from firebase_admin import auth as admin_auth

from flask import current_app

import concurrent.futures

from threading import Thread

def generate_firebase_login_token(user_unique_token):

	return admin_auth.create_custom_token(user_unique_token)


def firebase_login(user_unique_token):

	login_token = generate_firebase_login_token(user_unique_token)

	app = current_app._get_current_object()

	with concurrent.futures.ThreadPoolExecutor() as executor:

		future = executor.submit(async_login_to_firebase, login_token, app)

		return_value = future.result()

	return return_value

def async_login_to_firebase(login_token, app):

	with app.app_context():

		try:

			user_auth = current_app.config["FIREBASE_USER_APP_INSTANCE"].auth()

			return user_auth.sign_in_with_custom_token(login_token.decode('utf-8'))

		except:

			return False		
			


def user_uid(idToken):

	app = current_app._get_current_object()


	with concurrent.futures.ThreadPoolExecutor() as executor:

		future = executor.submit(get_user_uid, idToken, app)

		return_value = future.result()

	return return_value



def get_user_uid(idToken, app):

	with app.app_context():

		#try:

		user_auth = current_app.config["FIREBASE_USER_APP_INSTANCE"].auth()

		user_uid = user_auth.get_account_info(idToken)['users'][0]['localId']

		return user_uid

		#except:

			#return None




		









