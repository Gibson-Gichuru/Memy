from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(Form):

	email = StringField('email', validators = [DataRequired(), Length(1, 64), Email()])

	password = PasswordField('password', validators = [DataRequired()])

	remember_me = BooleanField('keep me logged in ')

	submit = SubmitField('log in ')