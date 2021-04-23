from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash, current_app
from flask_login import login_user
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, ContactForm
from ..models import User, Permission, Role

from flask_login import login_required, current_user

from ..decorators import admin_required, permission_required

from .. import db
from ..email import send_email

@main.route('/')
def index():

	return redirect(url_for('auth.login'))


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




@main.route('/home')
@login_required
def home():

	return render_template('home.html')

@main.route('/user/<username>')
def user(username):

	user = User.query.filter_by(username = username).first()

	if user is None:

		abort(404)

	return render_template('user.html', user = user)



@main.route('/edit-profile/', methods = ['GET', 'POST'])
@login_required
def edit_profile():

	form = EditProfileForm()

	if form.validate_on_submit():

		user = User.query.filter_by(username = current_user.username).first()

		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data

		db.session.add(user)

		user.update()

		flash('Your Profile has been updated')
		return redirect(url_for('.user', username = current_user.username))

	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me

	return render_template('edit_profile.html', form = form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):

	user = User.query.get_or_404(id)

	form = EditProfileAdminForm(user = user)

	if form.validate_on_submit():

		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data

		db.session.add(user)

		flash('The profile have been updated')

		return redirect(url_for('main.user', username = user.username))


	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me

	return render_template('edit_profile.html', form = form, user = user)

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
