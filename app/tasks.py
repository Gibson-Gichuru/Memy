import  os

import sys

import pyrebase
import firebase_admin


from rq import get_current_job
from app import create_app

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
app.app_context().push()

from app import db 

from app.models import Task, Post, File

from . utils import firebase_login

from . uploads import firebase_upload_file


import time


def _set_job_progress(progress):

	## get the current job the worker is handling

	job = get_current_job()

	if job:

		## update the job metadata progress

		job.meta['progress'] = progress
		job.save_meta()
		task = Task.query.get(job.get_id())

		## implement push notification functionality first

		"""

		task.user.add_notification('upload_progress', {'task_id': job.get_id(), 'progress':progress})"""


		### in case the progress key:value exceeds 100 it means the job was handled and completed

		if progress >= 100:

			## update the complete status of the task job to complete

			task.complete = True

		db.session.commit()



def upload_file_to_cloud(file_object,file_object_id):

	try:

		time.sleep(3)

		file = File.query.get(file_object_id)

		## login the given user to Firebase

		if file is not None:

			cloud_login = firebase_login(file.post.author.firebase_custom_token)

			## upload the given file

			firebase_upload_file(file_object, file.file_url, cloud_login['idToken'])

	except  Exception as e:

		app.logger.error('Unhandled exception', exc_info=sys.exc_info())
		## handle unexpected errors


	finally:

		## get the file URL from the cloud and update the file URL to database

		storage = app.config['FIREBASE_USER_APP_INSTANCE'].storage()

		local_url = file.file_url

		file.file_url = storage.child(local_url).get_url(file.post.author.firebase_uid)

		#update changes to database

		db.session.add(file)

		db.session.commit()

		## clean up the file from the local file system-storage

		os.remove(file_object)


		