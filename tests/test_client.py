import unittest

from app import create_app, db
from app.models import User, Role
from flask import url_for

class FlaskClientTestCase(unittest.TestCase):

	def setUp(self):

		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client(use_cookies = True)


	def tearDown(self):

		db.session.remove()
		db.drop_all()
		self.app_context.pop()


	def test_home_page(self):

		response = self.client.get(url_for('main.index'))
		self.assertTrue('Me.my' in response.get_data(as_text = True))


	def test_register_and_login(self):

		# register a new account

		response = self.client.post(url_for('auth.register'),
			data = {

				'email':'gibson@example.com',
				'password':'cat',
				'password2':'cat'

			})

		self.assertTrue(response.status_code == 302)

		#login to the account 

		response = self.client.post(url_for('auth.login'),
			data = {

				'email':'gibson@example.com',
				'password':'cat'

			}, follow_redirects = True)

		data = response.get_data(as_text=True)

		self.assertTrue('You have not confirmed your account yet.' in data)

		#send a confirmation token

		user = User.query.filter_by(email='gibson@example.com').first()
		token = user.generate_confirmation_token()

		response = self.client.post(url_for('auth.confirm', token=token)
			, follows_redirects = True)

		data = response.get_data(as_text = True)

		self.assertTrue("You have confired your account. Thanks!" in data)

		#logout 

		response = self.client.get(url_for('auth.logout'), follows_redirects = True)

		data = response.get_data(as_text = True)

		self.assertTrue('you have logged out')