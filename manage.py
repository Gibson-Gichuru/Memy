#!/usr/bin/env python
import os
import sys
COV = None 

if os.environ.get('FLASK_COVERAGE'):

	import coverage
	COV = coverage.coverage(branch =True, include='app/*')
	COV.start()

from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():

	return dict(app = app, db = db, User = User, Role = Role)


@manager.command
def test(coverage=False):
	"""Run The Unit Tests. """

	if coverage and not os.environ.get('FLASK_COVERAGE'):

		os.environ['FLASK_COVERAGE'] = '1'

		os.execvp(sys.executable, [sys.executable] + sys.argv)

	import unittest

	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity = 2).run(tests)

	if COV:

		COV.stop()
		COV.save()
		print('Coverage Summary')
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print('HTML version: file://{}/index.html'.format(covdir))

		COV.erase()


@manager.command
def deploy():

	from flask_migrate import upgrade
	from app.models import Role, User 

	upgrade()

	Role.insert_roles() 

	User.add_self_follows()



manager.add_command("shell", Shell(make_context = make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':

	manager.run()