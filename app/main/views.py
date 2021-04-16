from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from ..models import User, Permission

from flask_login import login_required, current_user

from ..decorators import admin_required, permission_required

from .. import db

@main.route('/', methods = ['GET', 'POST'])
def home():

	form = NameForm()

	if form.validate_on_submit():

		user = User.query.filter_by(username = form.name.data).first()

		if user is None:

			user = User(username = form.name.data)

			user.add(user)

			session['known'] = False

		else:
			
			session['known'] = True
		
		session['name'] = form.name.data

		form.name.data = ''


		return redirect(url_for('.home'))


	return render_template('home.html',form=form, name=session.get('name'),
							known=session.get('known', False),
							current_time=datetime.utcnow())

@main.route('/user/<username>')
def user(username):

	user = User.query.filter_by(username = username).first()

	if user is None:

		abort(404)

	return render_template('user.html', user = user)



@main.route('/edit-profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():

	form = EditProfileForm()

	if form.validate_on_submit():

		user = User.query.filter_by(username = current_user.username).first()

		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data

		db.session.add(user)

		flash('Your Profile has been updated')
		return redirect(url_for('.user', username = current_user.username))

	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me

	return render_template('edit_profile.html', form = form)


main.route('/edit-profile/<int:id>')
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
