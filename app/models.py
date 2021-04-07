from . import db


class DataManipulation:

	def add(self,resource):

		db.session.add(resource)

		return db.commit()

	def delete(self, resource):

		return db.session.delete(resource)

class Role(db.Model, DataManipulation):

	__tablename__ = 'roles'

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), unique = True)

	users = db.relationship('User', backref = 'role')


	def __repr__(self):

		return '<Role {}>'.format(self.name)


class User(db.Model, DataManipulation):

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), unique = True, index = True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):

		return '<User {}>'.format(self.username)