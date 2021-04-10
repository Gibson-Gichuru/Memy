from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from . import auth
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm

from . import auth

@auth.route('/login', methods = ['GET', 'POST'])
def login():

	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()

		if user is not None and user.verify_password(form.password.data):

			login_user(user, form.remember_me.data)

			return redirect(request.args.get('next') or url_for('main.home'))

		flash('Invalid username or password')

	return render_template('auth/login.html', form = form)



@auth.route('/register', methods = ['GET', 'POST'])
def register():

	form = RegistrationForm()

	if form.validate_on_submit():

		user = User(email = form.email.data, username = form.username.data,
			password = form.password.data)

		user.add(user)

		token = user.generate_confirmation_token()
		send_email(user.email, 'Confirm your Account', 'auth/email/confirm', user = user, token = token)

		flash('A Confirmation email has been sent to you by email')

		return redirect(url_for('main.home'))

	return render_template('auth/register.html', form = form)


@auth.route('/logout')
@login_required
def logout():

	logout_user()
	flash('you have logged out')

	return redirect(url_for('main.home'))
