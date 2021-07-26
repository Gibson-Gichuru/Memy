from flask_wtf import FlaskForm as Form
from flask import request
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    BooleanField,
    TextField,
    SelectField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_pagedown.fields import PageDownField

from ..models import User, Role


class NameForm(Form):

    name = StringField('Whatis your name', validators=[DataRequired()])
    submit = SubmitField('submit')


class EditProfileForm(Form):

    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('Bio')
    profile_pic = FileField(
        'Upload New Display Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
    )
    cover_pic = FileField(
        'Upload New Cover Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
    )
    email = StringField("email", validators=[Length(0, 64), Email()])
    password = PasswordField(
        "password", validators=[EqualTo("password2", message="password must match")]
    )
    password2 = PasswordField("confirm password")

    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):

    email = StringField("email", validators=[Length(0, 64), Email()])

    username = StringField(
        'Username',
        validators=[
            Length(0, 64),
            Regexp(
                '^[A-Za-z][A-Za-z0-9_.]*$',
                0,
                'Usename must consist of letters, numbers, dot or underscore',
            ),
        ],
    )

    confirmed = BooleanField('Confirmed')

    profile_pic = FileField(
        'Upload New Display Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
    )

    cover_pic = FileField(
        'Upload New Cover Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
    )

    role = SelectField('Role', coerce=int)

    name = StringField("Real Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField('About Me')

    password = PasswordField(
        "password", validators=[EqualTo("password2", message="password must match")]
    )
    password2 = PasswordField("confirm password")

    submit = SubmitField('Update')

    def __init__(self, user, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.role.choices = [
            (role.id, role.name) for role in Role.query.order_by(Role.name).all()
        ]

        self.user = user

    def validate_email(self, field):

        if (
            field.data != self.user.email
            and User.query.filter_by(email=field.data).first()
        ):

            raise ValidationError('Email Aready Registerd')

    def validate_username(self, field):

        if (
            field.data != self.user.username
            and User.query.filter_by(username=field.data).first()
        ):

            raise ValidationError('Username already in use')


class ContactForm(Form):

    name = StringField('name', validators=[DataRequired(), Length(1, 64)])

    email = StringField('email', validators=[DataRequired(), Length(1, 64), Email()])

    message = TextAreaField('message')

    submit = SubmitField('submit')


class PostForm(Form):

    body = PageDownField(validators=[DataRequired()])

    file_upload = FileField(
        '', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'mp4', 'gif'])]
    )

    submit = SubmitField("Post")


class SearchForm(Form):
	"""This form request handling is different from the other forms such that because
	we want to have our search url to contain as much data about the item we are searching 
	then we have to deal with Get request instead of the default Post request"""

    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):


    	##formdata in this context points t where Flask-WTF loads its data from 
    	## by default Flask-Wtf loads its data from request.form object for all Post requests
    	## but because we are using Get request to handle data we have to point Flask-Wtf to user
    	##requsts.agrs since data in a Get request is stored as a query String

        if 'formdata' not in kwargs:

            kwargs['formdata'] = request.args

        if 'csrf_enabled' not in kwargs:

            kwargs['csrf_enabled'] = False

        super(SearchForm, self).__init__(*args, **kwargs)


class CommentForm(Form):

    body = StringField("Comment", validators=[DataRequired()])

    submit = SubmitField('post')
