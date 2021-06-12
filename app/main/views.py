from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash, current_app, request, g
from flask_login import login_user
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, ContactForm, PostForm, SearchForm, CommentForm

from ..auth.forms import LoginForm, RegistrationForm

from ..models import User, Permission, Role, Post, Comment

from flask_login import login_required, current_user

from ..decorators import admin_required, permission_required

from .. import db
from ..email import send_email

from random import  choice , sample

from ..uploads import firebase_upload_file, rename_file, admin_file_upload_to_storage
from ..utils import firebase_login


@main.route('/', methods = ['GET', 'POST'])
def index():

	form = LoginForm()

	reg_form = RegistrationForm()

	page = request.args.get('page', 1, type = int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, 
		current_app.config['FLASKY_POSTS_PER_PAGE'], error_out = False)

	posts = pagination.items

	return render_template('index.html',posts = posts, pagination = pagination, form = form,
		reg_form = reg_form)


@main.route('/contacts', methods =["GET","POST"])
def contacts():

	form = ContactForm()

	if form.validate_on_submit():

		# send an email to the addmin
		send_email(current_app.config['FLASK_ADIM'],
		 "Message from a {}".format(form.name.data),
			"contacts/message", form = form )
		return redirect(url_for('main.index'))
	return render_template('contact.html', form = form)




@main.route('/home', methods = ['GET', 'POST'])
@login_required
def home():

	form = PostForm()

	comment_form = CommentForm()

	page = request.args.get('page', 1, type = int)

	if current_user.can(Permission.WRITE_ARTICLES) and form .validate_on_submit():

		post = Post(body = form.body.data, author = current_user._get_current_object())

		db.session.add(post)

		post.add(post)

		return redirect(url_for('main.home'))


	# show current user posts made by users they are following

	pagination = current_user.followed_posts.order_by(Post.timestamp.desc()).paginate(page,
		current_app.config['FLASKY_POSTS_PER_PAGE'], error_out = False)

	posts = pagination.items

	if current_user.user_following.count() == 0:

		users_to_follow = []

	else:
		random_follower = choice(current_user.user_following.all())

		if random_follower.user_following.count() >= 4:

			users_to_follow = sample(random_follower.user_following.all(),4)

		else:
			users_to_follow = random_follower.user_following.all()


	return render_template('home.html', form = form, 
		posts = posts, permission = Permission, 
		pagination = pagination, users_to_follow = users_to_follow, comment_form = comment_form)

@main.route('/user/<username>')
def user(username):


	page = request.args.get('page', 1, type=int)

	user = User.query.filter_by(username = username).first()

	if user is None:

		abort(404)

	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, 
		current_app.config['FLASKY_POSTS_PER_PAGE'], error_out = False)

	posts = pagination.items

	return render_template('user.html', user = user, posts = posts, 
		pagination = pagination, Permission = Permission)

@main.route('/edit-profile/', methods = ['GET', 'POST'])
@login_required
def edit_profile():

	form = EditProfileForm()

	if form.validate_on_submit():

		user = User.query.filter_by(username = current_user.username).first()

		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data

		if form.password.data != "":

			user.password = form.password.data

		if form.email.data != user.email:

			user.email = form.email.data
			user.confirmed = False


		if form.profile_pic.data is not None:

			login_to_to_firebase = firebase_login(user.firebase_custom_token)

			cloud_file_name = rename_file(form.profile_pic.data)

			firebase_upload_file(cloud_file_name,
			 "/data/{}/profile/".format(user.firebase_uid), login_to_to_firebase['idToken'])

			user.profile_pic_id = cloud_file_name.filename

		if form.cover_pic.data is not None:

			login_to_to_firebase = firebase_login(user.firebase_custom_token)

			cloud_file_name = rename_file(form.cover_pic.data)

			firebase_upload_file(cloud_file_name,
			 "/data/{}/profile/".format(user.firebase_uid), login_to_to_firebase['idToken'])

			user.cover_photo_id = cloud_file_name.filename


		db.session.add(user)

		user.update()

		flash('Your Profile has been updated')
		return redirect(url_for('.user', username = current_user.username))

	return render_template('edit_profile.html', form = form)


@main.route('/edit-admin-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):

	user = User.query.get_or_404(id)

	form = EditProfileAdminForm(user = user)


	if form.validate_on_submit():

		if form.email.data != user.email:

			user.email = form.email.data 
			user.confirmed = False


		if form.username != user.username:
			user.username = form.username.data

		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data


		if form.profile_pic.data is not None:

			cloud_file_name = rename_file(form.profile_pic.data)
			admin_file_upload_to_storage(cloud_file_name, 
				"/data/{}/profile/".format(user.firebase_uid))

			user.profile_pic_id = cloud_file_name.filename


		if form.cover_pic.data is not None:

			cloud_file_name = rename_file(form.cover_pic.data)
			admin_file_upload_to_storage(cloud_file_name, 
				"/data/{}/profile/".format(user.firebase_uid))

			user.cover_photo_id = cloud_file_name.filename



		db.session.add(user)
		user.update()

		flash('The profile have been updated')

		return redirect(url_for('main.user', username = user.username))


	form.email.data = user.email 
	form.username.data = user.username
	form.name.data = user.name
	form.location.data = user.location 
	form.about_me.data = user.about_me

	return render_template('edit_profile_admin.html', form = form, user = user)


@main.route('/post/<int:id>')
def post(id):

	post = Post.query.get_or_404(id)

	comment_form = CommentForm()

	return render_template('post.html', posts = [post], comment_form = comment_form, Permission = Permission)


@main.route('/edit/<int:id>', methods = ['GET', 'POST'])
def edit(id):

	post = Post.query.get_or_404(id)

	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)

	form = PostForm()

	if form.validate_on_submit():

		post.body = form.body.data
		post.update()
		flash('Post have been updated')
		return redirect(url_for('main.post', id = post.id))

	form.body.data = post.body 

	return render_template('edit_post.html', form = form)


@main.route('/comment/<int:id>', methods = ['GET', 'POST'])
@login_required
def comment(id):

	post = Post.query.get_or_404(id)

	form = CommentForm()

	if form.validate_on_submit():

		comment = Comment(body = form.body.data, post = post, 
			author = current_user._get_current_object())

		db.session.add(comment)
		db.session.commit()

		flash("your view in the post have been published")

		return redirect(url_for('main.home'))

	return redirect(url_for('main.home'))


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comment_enabled(id):

	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	db.session.commit()

	return redirect(url_for('main.post', id = comment.post_id))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comment_disabled(id):

	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	db.session.commit()

	return redirect(url_for('main.post', id = comment.post_id))

@main.route('/delete/<int:id>')
def delete_post(id):

	post = Post.query.get_or_404(id)

	if current_user !=post.author and not current_user.can(Permission.ADMINISTER):

		abort(403)

	post.delete(post)


	return redirect(url_for('main.home'))


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username = username).first()

	if user is None:

		flash("Invalid User")
		return redirect(url_for('main.home'))

	if current_user.is_following(user):

		flash("You are already following {}".format(username))

		return redirect(url_for('main.user', username = username))

	current_user.follow(user)
	flash("You are now following {}".format(username))

	return redirect(url_for('main.user', username = username))


@main.route('/followers/<username>')
def followers(username):

	user = User.query.filter_by(username = username).first()

	if user is None:

		flash('Invalid User')

		if current_user.is_authenticated:

			return redirect(url_for('main.home'))

		return redirect(url_for('main.index'))

	page = requets.args.get('page', 1 , type=int)

	pagination = user.followers.paginate(page, per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out = False)

	follows =  [{'user':item.follower, 'timestamp':item.timestamp} for item in pagination.items]

	return render_template('follower.html', user = user, title = "Followers of", endpoint = 'main.followers',
		pagination = pagination, follows = follows)

@main.route('/following/<username>')
def following(username):

	user = User.query.filter_by(username = username).first()

	if user is None:

		flash('Invalid User')

		if current_user.is_authenticated:

			return redirect(url_for('main.home'))

		return redirect(url_for('main.index'))

	page = requets.args.get('page', 1 , type=int)

	pagination = user.followers.paginate(page, per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out = False)

	following =  [{'user':item.followed, 'timestamp':item.timestamp} for item in pagination.items]

	return render_template('follower.html', user = user, title = "Followers of", endpoint = 'main.following',
		pagination = pagination, following = following)


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):

	user = User.query.filter_by(username = username).first()


	if user is not None and current_user.is_following(user):

		current_user.unfollow(user)

		return redirect(url_for('main.user', username = username))

	return redirect(url_for('main.home'))



@main.route("/admin")
@login_required
@admin_required
def for_admins_only():

	return "for administrator only"


@main.route("/moderator")
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():

	return "for moderators only"


@main.route('/upload', methods=['GET', 'POST'])
def upload_file():

	return render_template('upload.html')