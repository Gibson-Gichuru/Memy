from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextField
from wtforms.validators import DataRequired, Email, Length


class NameForm(Form):

	name = StringField('Whatis your name', validators = [DataRequired()])
	submit = SubmitField('submit')


class EditProfileForm(Form):

	name = StringField('Real name', validators = [Length(0,64)])
	location = StringField('Location', validators = [Length(0,64)])
	about_me = TextField('About Me')
	submit = SubmitField('Submit')