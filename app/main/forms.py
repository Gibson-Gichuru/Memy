from flask_wtf import FlaskForm as Form
from wtforms import (StringField, SubmitField, PasswordField, BooleanField, TextField, SelectField, TextAreaField)
from wtforms.validators import DataRequired, Email, Length, Regexp
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_pagedown.fields import PageDownField

from ..models import User, Role



class NameForm(Form):

	name = StringField('Whatis your name', validators = [DataRequired()])
	submit = SubmitField('submit')


class EditProfileForm(Form):

	name = StringField('Real name', validators = [Length(0,64)])
	location = StringField('Location', validators = [Length(0,64)])
	about_me = TextField('About Me')
	profile_pic = FileField('profile', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
	submit = SubmitField('Submit')
	


class EditProfileAdminForm(Form):

	email = StringField('Email', validators = [DataRequired(), Length(1,64), Email()])

	username = StringField('Username', validators = [DataRequired(), Length(1,64),\
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
			'Usename must consist of letters, numbers, dot or underscore')])

	confirmed = BooleanField('Confirmed')

	role = SelectField('Role', coerce = int)

	name = StringField("Real Name", validators = [Length(0,64)])
	location = StringField("Location", validators = [Length(0,64)])
	about_me = TextField('About Me')
	submit = SubmitField('Update')


	def __init__(self, user, *args, **kwargs):

		super(EditProfileAdminForm).__init__(*args, **kwargs)

		self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]

		self.user = user

	def validate_email(self, field):

		if field.data != self.user.email and User.query.filter_by(email=field.data).first():

			raise ValidationError('Email Aready Registerd')


	def validate_username(self, field):

		if field.data != self.user.username and User.query.filter_by(username = field.data).first():

			raise ValidationError('Username already in use')


class ContactForm(Form):

	name = StringField('name', validators=[DataRequired(), Length(1,64)])

	email = StringField('email', validators = [DataRequired(), Length(1,64), Email()])

	message = TextAreaField('message')

	submit = SubmitField('submit')


class PostForm(Form):

	body = TextAreaField(validators = [DataRequired()])

	submit = SubmitField("Post")


class SearchForm(Form):

	username = StringField('username', validators =[DataRequired()])

	search = SubmitField('search')