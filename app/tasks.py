from rq import get_current_job
from app import create_app

app = create_app()
app.app_context().push()

from app import db 

from app.models import Task


def _set_job_progress(progress):

	## geth the current job the worker is handling

	job = get_current_job()

	if job:

		## update the job metadata progress

		job.meta['progress'] = progress
		job.save_meta()
		task = Task.query.get(job.get_id())

		## implement push notification functionality first

		"""

		task.user.add_notification('upload_progress', {'task_id': job.get_id(), 'progress':progress})"""


		### incase the progress key:value exceeds 100 it means the job was handled and completed

		if progress >= 100:

			## update the complete status of the task job to complete

			task.complete = True

		db.session.commit()



def upload_file_to_cloud():

	try:

		## login the given user to firebase

		## upload the given file

	except :

		## handle unexcected errors


	finally:

		## clean up the file from the local file system-storage