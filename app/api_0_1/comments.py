from flask import jsonify, request, current_app, url_for
from ..models import Comment, Permission, Post
from .authentication import auth
from .decorators import permission_required
from . import api
from .. import db


@api.route('/comments/<int:id>')
@auth.login_required
def get_post_comments(id):

	page = request.args.get('page', 1, type = int)

	post = Post.query.get_or_404(id)

	pagination = post.comment.paginate(page,
		per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out = False)

	comments = pagination.items

	prev= None

	if pagination.has_prev: 

		pre = url_for('api.get_post_comments', id = id, page = page-1, _external=True)

	next = None

	if pagination.has_next:

		next = url_for('api.get_post_comments', id = id, page = page+1, _external = True)

	return jsonify({

		'comments':[comment.to_json() for comment in comments],
		'prev': prev,
		'next': next,
		'count': pagination.total

		})


@api.route('/write_comment/<int:id>', methods=['POST'])
@permission_required(Permission.COMMENT)
def comment(id):

	post = Post.query.get_or_404(id)

	comment = Comment.from_json(request.json)
	comment.author = g.current_user
	comment.post = post
	db.session.add(comment)
	db.session.commit()

	return jsonify(comment.to_json(), 200,
		{'location':url_for('api.get_post_comments', id  = post.id, _external = True)})