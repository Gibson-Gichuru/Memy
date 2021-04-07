import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	
	SECRET_KEY = os.environ.get('SECRET_KEY') 

	SQLALCHEMY_COMMITON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	FLASK_MAIL_SUBJECT_PREFIX = '[Flasky]'
	FLASK_MAIL_SENDER = 'Flask Admin <flaskyadmin@gmail.com>'
	FLASK_ADMIN = os.environ.get('FLASK_ADMIN')

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	
	DEBUG = True

	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TSL = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):

	TESTING = True

	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):

	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'data.sqlte')



config = dict(developent = DevelopmentConfig, 
	testing = TestingConfig, 
	production = ProductionConfig, 
	default = DevelopmentConfig)