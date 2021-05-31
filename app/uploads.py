from flask import request, current_app
from threading import Thread

def send_async_files(profile_pic)
	api_request = request.post(api_url, headers = requred_headers, file = profile_pic)

def upload_profile_pic(profile_pic):

	api_url = 'https://api.base-api.io/v1/images'

	requred_headers = {'Authorization':current_app.config['FILE_UPLOAD_API_AUTH_KEY']}

	file_upload_thred = Thread(target = send_async_files, args = [profile_pic])

	return file_upload_thred


