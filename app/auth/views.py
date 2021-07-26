from flask import render_template, redirect, request, url_for, flash, g
from flask_login import login_user, login_required, logout_user, current_user
from . import auth
from ..models import User
from ..email import send_email
from .forms import RegistrationForm, ForgotPasswordForm, ResetPasswordForm, LoginForm

from . import auth

from .. import db

from ..utils import firebase_login, user_uid

from app.main.forms import SearchForm


@auth.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data):

            login_user(user, form.remember_me.data)

            user_login_to_firebase = firebase_login(user.firebase_custom_token)

            next = request.args.get('next')

            if next is None or not next.startswith('/'):

                next = url_for('main.home')
            return redirect(next)

        else:

            flash("Invalid Email or password")

    return render_template('auth/login.html', form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():

        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        )

        db.session.add(user)
        user.follow(user)
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            "Confirm your Account",
            "auth/email/confirm",
            user=user,
            token=token,
        )

        flash("A Confirmation email has been sent to you by email")

        return redirect(url_for("auth.login"))

    return render_template('auth/register.html', form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):

    if current_user.confirmed:

        return redirect(url_for("main.home"))

    if current_user.confirm(token):

        user_login_to_firebase = firebase_login(current_user.firebase_custom_token)

        current_user.firebase_uid = user_uid(user_login_to_firebase['idToken'])

        current_user.idToken = user_login_to_firebase['idToken']

        db.session.add(current_user)

        flash("You have confired your account. Thanks!")

    else:

        flash("The activation link is invalid or has expired")

    return redirect(url_for("auth.login"))


@auth.before_app_request
def before_request():

    if current_user.is_authenticated:
        current_user.ping()

        # make the search form visible in any authetication required route within our application
        g.search_form = SearchForm()

    if (
        current_user.is_authenticated
        and not current_user.confirmed
        and request.endpoint[:5] != "auth."
    ):

        return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():

    if current_user.is_anonymous or current_user.confirmed:

        return redirect("auth.login")

    return render_template("auth/unconfirmed.html")


@auth.route("/confirm")
@login_required
def resend_confirmation():

    token = current_user.generate_confirmation_token()

    send_email(
        current_user.email,
        "Confirm Your Account",
        "auth/email/confirm",
        user=current_user,
        token=token,
    )
    flash("A new Confirmation email has been sent to {}".format(current_user.email))

    return redirect(url_for("auth.login"))


@auth.route("/forgot_password/", methods=['GET', 'POST'])
def forgot_password():

    form = ForgotPasswordForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        token = user.generate_reset_token()

        send_email(
            form.email.data,
            "Reset password",
            "auth/email/reset_password",
            user=user,
            token=token,
        )

        flash("a password reset link have been sent to you by email")

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html", form=form)


@auth.route("/confirm_reset/<token>", methods=['GET', 'POST'])
def confirm_reset(token):

    if not current_user.is_anonymous:

        return redirect(url_for("auth.login"))

    form = ResetPasswordForm()

    if form.validate_on_submit():

        if User.reset_password(token, form.password.data):

            flash("Your password have been reset, you can now log in")

            return redirect(url_for("auth.login"))

        else:

            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)


@auth.route("/logout")
@login_required
def logout():

    logout_user()
    flash("you have logged out")

    return redirect(url_for("main.index"))
