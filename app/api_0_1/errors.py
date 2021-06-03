#Error handler that returns appropriate responses depending on the client needs

from flask import render_template, jsonify, request

from ..main import main

@main.app_errorhandler(404)
def page_not_found(e):

	if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:

		response = jsonify({"Error":"not found"})

		response.status_code = 404

		return response

	return render_template('errors/404.html'), 404



@main.app_errorhandler(404)
def internal_server_error(e):

	if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:

		response = jsonify({"Erro":"Intenal server error"})

		response.status_code = 500

		return response

	return render_template('errors/500.html'), 500


def forbidden_errror(message):

	response = jsonify({"Error":"forbidden", "Message":message})
	response.status_code = 404

	return response


def unauthorised(message):

	response = jsonify({"Error":"unauthorised", "Message":"Not Authorised to view the requested resource"})

	response.status_code = 401

	return response


@api.error_handler(ValidationError)
def validation_error(e):

	return bad_request(e.args[0])

