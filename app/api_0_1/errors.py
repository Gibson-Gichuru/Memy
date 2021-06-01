#Error handler that returns appropriate responses depending on the client needs

from flask import render_template, jsonify, request

from .app.main import main

@main.app_error_handler(404)
def page_not_found(e):

	if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:

		response = jsonify({"Error":"not found"})

		response.status_code = 404

		return response

	return render_template('errors/404.html'), 404



@main.app_error_handler(500):
def internal_server_error(e):

	if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:

		response = jsonify({"Erro":"Intenal server error"})

		response.status_code = 500

		return response

	return render_template('errors/500.html'), 500