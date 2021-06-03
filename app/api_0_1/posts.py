from flask import jsonify, request, current_app, url_for

from ..models import Post, Permission

from .authentication import auth
from .decorators import permission_required
from . import api
from .. import db



@api.route('/posts/')
@auth.login_required
def get_posts():

	page = request.args.get('page', 1, type=int)

	pagination = Post.query.paginate(page,\
	 per_page = current_app.config['FLASKY_POSTS_PER_PAGE'], \
	 error_out = False)

	posts = pagination.items

	prev = None

	if pagination.has_prev :

		prev = url_for('api.get_posts', page=page-1, _external=True)

	next = None

	if pagination.has_next:

		next = url_for('api.get_posts', page=page+1, _external=True)

	return jsonify({

			'posts': [post.to_json() for post in posts],
			'prev':prev,
			'next':next,
			'count': pagination.total
		})


@api.route('/post/<int:id>')
@auth.login_required
def get_post(id):

	post = Post.query.get_or_404(id)

	return jsonify(post.to_json())

#Register new resources


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():

	post = Post.from_json(request.json)
	post.author = g.current_user
	db.session.add(post)
	db.session.commit()

	return jsonify(post.to_json(), 201, {'location':url_for('api.get_post', \
		id = post.id, _external = True)})


#Edit a post resource

@api.route('/posts/<int:id>', methods = ['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):

	post = Post.query.get_or_404(id)

	if g.current_user != post.author and g.current_user.can(Permission.ADMINISTER):

		return forbidden("Inserfficient Permissions")


	post.body = request.json.get('body', post.body)

	db.session.add(post)

	db.session.commit()

	return jsonify(post.to_json())


# Delete a resource

@api.route('/delete_post/<int:id>', methods=['DELETE'])
@permission_required(Permission.WRITE_ARTICLES)
def delete_post(id):

	post = Post.query.get_or_404(id)

	if g.current_user != post.author and g.current_user.can(Permission.ADMINISTER):

		return forbidden('Inserfficient Permissions')

	db.session.delete(post)

	db.session.commit()

	return jsonify({"message":"post deleted", "code":202})