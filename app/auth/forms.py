from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from wtforms import ValidationError
from ..models import User



class LoginForm(Form):

    email = StringField("email", validators=[DataRequired(), Length(1, 64), Email()])

    password = PasswordField("password", validators=[DataRequired()])

    remember_me = BooleanField("keep me logged in ")

    submit = SubmitField("log in")


class RegistrationForm(Form):

    email = StringField("email", validators=[DataRequired(), Length(1, 64), Email()])

    username = StringField(
        "username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have onyl \
							letters, numbers, dots or underscore",
            ),
        ],
    )

    password = PasswordField(
        "password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="password must match"),
        ],
    )

    password2 = PasswordField("confirm password", validators=[DataRequired()])

    submit = SubmitField("Regiser")

    # custom validators

    def validate_email(self, field):

        if User.query.filter_by(email=field.data).first():

            raise ValidationError("Email aready registered")

    def validate_username(self, field):

        if User.query.filter_by(username=field.data).first():

            raise ValidationError("Username aready in use")


class ForgotPasswordForm(Form):

    email = StringField("email", validators=[DataRequired(), Length(1, 64), Email()])

    submit = SubmitField('Send')

    def validate_email(self, field):

        if User.query.filter_by(email = field.data).first() is None:

            raise ValidationError("Give a valid email address")


class ResetPasswordForm(Form):

    password = PasswordField(
        "password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="password must match"),
        ],
    )

    password2 = PasswordField("confirm password", validators=[DataRequired()])

    submit = SubmitField("Reset Password")
