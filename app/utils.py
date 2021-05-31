
import firebase_admin
from firebase_admin import credentials


def firebase_app_initiate():

	cred = credentials.Certificate('house-of-memes-firebase-adminsdk-qinz4-4191030797.json')

	return firebase_admin.initialize_app(cred)



