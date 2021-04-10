from . import db
from . import login_manager

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from flask import current_app

#call back function
@login_manager.user_loader
def load_user(user_id):

	return User.query.get(int(user_id))


class DataManipulation:

	def add(self,resource):

		db.session.add(resource)

		return db.session.commit()

	def delete(self, resource):

		db.session.delete(resource)

		return db.session.commit()

	def update(self, resource):

		return db.session.commit()

class Role(db.Model, DataManipulation):

	__tablename__ = 'roles'

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), unique = True)

	users = db.relationship('User', backref = 'role')


	def __repr__(self):

		return '<Role {}>'.format(self.name)


class User(db.Model, DataManipulation, UserMixin):

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(64), unique = True, index = True)
	username = db.Column(db.String(64), unique = True, index = True)
	password_hash = db.Column(db.String(130))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	confirmed = db.Column(db.Boolean, default = False)

	@property
	def password(self):
		raise AttributeError("Password is not a readable attribute")

	@password.setter
	def password(self, password):

		self.password_hash = generate_password_hash(password)


	def verify_password(self, password):

		return check_password_hash(self.password_hash, password)


	def generate_confirmation_token(self, expiration = 3600):

		s = Serializer(current_app.config['SECRET_KEY'], expiration)

		return s.dumps({'confirm':self.id})


	def confirm(self, token):

		s = Serializer(current_app.config['SECRET_KEY'])

		try:

			data = s.loads(token)

		except:

			return False

		if data.get('confirm') != self.id:

			return False

		self.confirm = True

		db.session.add(self)

		return True


	
	

	def __repr__(self):

		return '<User {}>'.format(self.username)



