from flask_httpauth import HTTPBasicAuth 

from .errors import forbidden_errror, unauthorised

from . import api

from flask import jsonify

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):

	if email_or_token == "":

		g.current_user = AnonymousUser()
		return True 

	if password == "":

		g.current_user = User.verify_auth_token(email_or_token)
		g.token_used = True 

		return g.current_user is not None

	user = User.query.filter_by(email=email_or_token).first()

	if not user:

		return False

	g.current_user = user
	g.token_used = False

	return user.verify_password(password)


@auth.error_handler
def auth_error():

	return unauthorised('Invalide credentials')


#Protect all the routes in this blueprint

@api.before_request
@auth.login_required
def before_request():

	if not g.current_user.is_anonymous and not g.current_user.confirmed:

		return forbidden_errror("Unconfiremed Account")


@api.route('/token')
def get_token():

	"""Ensure that the client cannot use an old token to request for a new
	authentication token,
	Only email password authentication combo can be used to request for an
	autheentication password"""

	if g.current_user.is_anonymous or g.token_used:

		return unauthorised('Invalid credentials')

	return jsonify({"token":g.current_user.generate_auth_token(expiration = 3600),"expiration":3600})



