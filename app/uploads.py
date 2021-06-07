from flask import request, current_app, url_for
from threading import Thread

import hashlib

import os

def rename_file(user_file):

	old_name = os.path.splitext(user_file.filename)[0]

	extention = os.path.splitext(user_file.filename)[1]

	safe_name = hashlib.md5(old_name.encode('utf-8')).hexdigest()

	user_file.filename = '{}{}'.format(safe_name,extention)

	return [user_file,safe_name]

def firebase_upload_file(file_to_upload, cloud_directory, idToken):

	app = current_app._get_current_object()


	file_to_upload.save(os.path.join(current_app.config["UPLOAD_PATH"], file_to_upload.filename)) 

	full_path = cloud_directory + "{}".format(file_to_upload.filename)


	upload_file = os.path.join(current_app.config["UPLOAD_PATH"], file_to_upload.filename)

	upload_thread = Thread(target=async_file_upload_to_firebase, 
		args=[full_path, upload_file, app, idToken])

	upload_thread.start()

	return upload_thread


def async_file_upload_to_firebase(full_path, file_to_upload, app, idToken):

	with app.app_context():

		storage = current_app.config['FIREBASE_USER_APP_INSTANCE'].storage()

		storage.child(full_path).put(file_to_upload, idToken)

		os.remove(file_to_upload)
