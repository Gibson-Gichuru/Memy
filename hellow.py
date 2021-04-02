from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required



import datetime


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config['SECRET_KEY'] = 'dfwwe34.-435435pdfgl6u7were35]pty[py.ng;tyu-54735'
@app.route('/', methods = ['GET', 'POST'])
def home():

	form = NameForm()

	if form.validate_on_submit():
		session['name']= form.name.data
		return redirect(url_for('home'))
	return render_template('home.html', form = form, name = session.get('name'))

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

	name = StringField('what is your name', validators = [Required()])
	submit = SubmitField('submit')

if __name__ == '__main__':

    app.run(debug = True)
