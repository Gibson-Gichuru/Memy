from flask import jsonify, request

from ..models import Post, Permission

from .authentication import auth
from .decorators import permission_required
from .import api
from .. import db



@api.route('/posts/')
@auth.login_required
def get_posts():

	posts = Post.query.all()

	return jsonify({'posts':[post.to_json() for post in posts]})


@api.route('/posts/<int:id>')
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

