from flask import current_app, url_for, jsonify, request
from ..models import User, Permission

from .decorators import permission_required
from . import api
from .authentication import auth


@api.route('/user/<int:id>')
@auth.login_required
def get_user(id):

	user = User.query.get_or_404(id)

	return jsonify(user.to_json())


@api.route('/user/followers/<int:id>')
@auth.login_required
def get_user_followers(id):

	page = request.args.get('page', 1, type=int)

	user = User.query.get_or_404(id)

	pagination = user.user_followers.paginate(page, 
		per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
		error_out = False)


	followers = pagination.items 

	prev = None 

	if pagination.has_prev:

		prev = url_for('api.get_user_followers', id = user.id, page = page-1, _external = True)

	next = None 

	if pagination.has_next:

		next = url_for('api.get_user_followers', id = user.id, page = page+1, _external = True)


	return jsonify({

			'followers':[follower.to_json() for follower in followers],
			'prev':prev,
			'next':next,
			'count':pagination.total
		})


@api.route('/user/following/<int:id>')
@auth.login_required
def get_user_following(id):

	page = request.args.get('page', 1, type=int)

	user = User.query.get_or_404(id)

	pagination = user.user_following.paginate(page, 
		per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
		error_out = False)


	followering = pagination.items 

	prev = None 

	if pagination.has_prev:

		prev = url_for('api.get_user_following', id = user.id, page = page-1, _external = True)

	next = None 

	if pagination.has_next:

		next = url_for('api.get_user_following', id = user.id, page = page+1, _external = True)


	return jsonify({

			'following':[followed.to_json() for followed in followering],
			'prev':prev,
			'next':next,
			'count':pagination.total
		})








