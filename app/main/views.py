from datetime import datetime
from flask import render_template, session, redirect, url_for, abort
from . import main
from .forms import NameForm
from ..models import User, Permission

from flask_login import login_required

from ..decorators import admin_required, permission_required

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
