from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


import os
import datetime


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'dfwwe34.-435435pdfgl6u7were35]pty[py.ng;tyu-54735'
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite3:///' + os.path.join(basedir, 'data.sqlite3')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db =SQLAlchemy(app)

@app.route('/', methods = ['GET', 'POST'])
def home():

	form = NameForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username = form.name.data)

		if user is None:

			user = User(username = form.name.data)
			db.session.add(user)
			session['known'] = False

		else:
			
			session['known'] = True

		session['name'] = form.name.data
		form.name.data = ''

		return redirect(url_for('home'))		
	return render_template('home.html', form = form, name = session.get('name'),
		known = session.get('known', False))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name = name)


@app.errorhandler(404)
def page_not_found(e):

	return render_template('400.html') ,404


@app.errorhandler(500)
def internal_server_error(e):

	return render_template('500.html') ,500




class NameForm(Form):

	name = StringField('what is your name', validators = [DataRequired()])
	submit = SubmitField('submit')


class Role(db.Model):

	__tablename__  = "roles"

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(65), unique = True, nullable = False)

	users = db.relationship('User', backref='role', lazy='dynamic')

	def __repr__(self):

		return '<Role {}>'.format(self.name)


class User(db.Model):

	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(54), unique = True, index = True)
	role_id = db.Column(db.Integer(), db.ForeignKey('roles.id'))

	def __repr__(self):

		return '<User {}>'.format(self.username)

if __name__ == '__main__':

    app.run(debug = True)
