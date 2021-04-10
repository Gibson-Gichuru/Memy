from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
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


@auth.route('/confirm/<token>')
@login_required
def confirm(token):

	if current_user.confirmed:

		return redirect(url_for('main.home'))

	if current_user.confirm(token):

		flash('You have confired your account. Thenks!')

	else:
		
		flash('The activation link is invalid or has expired')

	return redirect(url_for('main.home'))


@auth.before_app_request
def before_request():

	if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.':

		return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():

	if current_user.is_anonymous or current_user.confirmed:

		return redirect('main.home')

	return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():

	token = current_user.generate_confirmation_token()

	send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user = current_user, token = token)
	flash('A new Confirmation email has been sent to {}'.format(current_user.email))

	return redirect(url_for('main.home'))

	


@auth.route('/logout')
@login_required
def logout():

	logout_user()
	flash('you have logged out')

	return redirect(url_for('main.home'))
