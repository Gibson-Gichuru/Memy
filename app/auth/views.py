from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from . import auth
from ..models import User
from .forms import LoginForm

from . import auth

@auth.route('/login')
def login():

	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()

		if user is not None and user.verify_password(form.password.data):

			login_user(user, form.remember_me.data)

			return redirect(request.args('next') or url_for('main.home'))

		flash('Invalid username or password')

	return render_template('auth/login.html', form = form)


@auth.route('/logout')
@login_required
def logout():

	logout_user()
	flash('you have logged out')

	return redirect(url_for('main.home'))
