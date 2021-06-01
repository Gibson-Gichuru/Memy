from flask_httpauth import HTTPBasicAuth 

from .errors import forbidden_errror, unauthorised

from . import api

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email, password):

	if email == "":

		g.current_user = AnonymousUser()
		return True 

	user = User.query.filter_by(email=email).first()

	if not user:

		return False

	g.current_user = user

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



