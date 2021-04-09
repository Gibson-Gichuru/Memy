from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email


class NameForm(Form):

	name = StringField('Whatis your name', validators = [DataRequired()])
	submit = SubmitField('submit')

