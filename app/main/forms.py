from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(Form):

	name = StringField('Whatis your name', validators = [DataRequired()])
	submit = SubmitField('submit')