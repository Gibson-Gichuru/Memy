from flask import request, current_app, url_for
from firebase_admin import storage
from threading import Thread

import hashlib

import os

def rename_file(user_file):

	old_name = os.path.splitext(user_file.filename)[0]

	extention = os.path.splitext(user_file.filename)[1]

	safe_name = hashlib.md5(old_name.encode('utf-8')).hexdigest()

	user_file.filename = '{}{}'.format(safe_name,extention)

	return user_file

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

		storage = current_app.firebase_user_instance.storage()

		storage.child(full_path).put(file_to_upload, idToken)

		os.remove(file_to_upload)



def admin_file_upload_to_storage(file_to_upload, cloud_directory):

	app = current_app._get_current_object()

	file_to_upload.save(os.path.join(current_app.config["UPLOAD_PATH"], file_to_upload.filename)) 

	full_path = cloud_directory + "{}".format(file_to_upload.filename)


	upload_file = os.path.join(current_app.config["UPLOAD_PATH"], file_to_upload.filename)

	upload_thread = Thread(target=admin_firebase_async_file_upload, 
		args=[full_path, upload_file, app])

	upload_thread.start()

	return upload_thread


def admin_firebase_async_file_upload(full_path, upload_file, app):

	with app.app_context():

		storage = current_app.firebase_admin_instance.storage()

		storage.child(full_path).put(upload_file)

		os.remove(upload_file)


def delete_uploaded_files(file_path):

	app = current_app._get_current_object()

	delete_file_thread = Thread(target = async_file_delete, args = [file_path, app])

	delete_file_thread.start()

	return delete_file_thread 

def async_file_delete(file_path, app):

	with app.app_context():

		storage = current_app.firebase_user_instance.storage()

		try:

			storage.delete(file_path)

		except:

			pass




