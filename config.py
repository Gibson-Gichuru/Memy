import os

basedir = os.path.abspath(os.path.dirname(__file__))

import pyrebase


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_COMMITON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASK_MAIL_SUBJECT_PREFIX = '[Me.My]'
    FLASK_MAIL_SENDER = 'Flask Admin {}'.format(os.environ.get('MAIL_USERNAME'))
    FLASK_ADMIN = os.environ.get('FLASK_ADMIN')
    FLASKY_POSTS_PER_PAGE = 5
    FLASKY_FOLLOWERS_PER_PAGE = 10
    FIREBASE_CONFIG = dict(
        apiKey="AIzaSyDjODHfV_kxeoXgalnfaCyiyd38_EuBBds",
        authDomain="house-of-memes.firebaseapp.com",
        projectId="house-of-memes",
        storageBucket="house-of-memes.appspot.com",
        databaseURL="https://house-of-memes-default-rtdb.firebaseio.com/",
        messagingSenderId="737530410440",
        appId="1:737530410440:web:21441705198ae5fd46bcfd",
        measurementId="G-0SXPFWWD1G",
        serviceAccount=os.path.join(basedir, 'firebase_admin_config.json'),
    )

    FIREBASE_USER_APP_INSTANCE = pyrebase.initialize_app(FIREBASE_CONFIG)
    MAX_CONTENT_LENGTH = 1024 * 1024 * 10
    UPLOAD_PATH = os.path.join(basedir, "uploads")

    SSL_DISABLE = True

    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")

    ELASTICSEARCH_USERNAME = os.environ.get("ELASTICSEARCH_USERNAME")
    ELASTICSEARCH_PASSWORD = os.environ.get('ELASTICSEARCH_PASSWORD')

    @staticmethod
    def init_app(app):

        pass


class DevelopmentConfig(Config):

    DEBUG = True
    USE_RELOADER = False

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL'
    ) or "mysql+pymysql://{}:{}@localhost/{}".format(
        os.environ.get("DATABASE_USERNAME"),
        os.environ.get("DATABASE_PASSWORD"),
        os.environ.get("DATABASE_NAME"),
    )


class TestingConfig(Config):

    TESTING = True

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL'
    ) or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

    WTF_CSRF_ENABLED = False

    @staticmethod
    def init_app(app):

        pass


class ProductionConfig(Config):

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) or \
    #'sqlite:///' + os.path.join(basedir, 'data.sqlte')

    @classmethod
    def init_app(cls, app):

        Config.init_app(app)

        # email errors to the administrator

        import logging
        from logging.handlers import SMTPHandler

        credentials = None

        secure = None

        if getattr(cls, "MAIL_USERNAME", None) is not None:

            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)

            if getattr(cls, 'MAIL_USE_TLS', None):

                secure = ()

        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASK_MAIL_SENDER,
            toaddrs=[cls.FLASK_ADMIN],
            subject=cls.FLASK_MAIL_SUBJECT_PREFIX + 'Application Error',
            credentials=credentials,
            secure=secure,
        )

        mail_handler.setLevel(logging.ERROR)

        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):

        ProductionConfig.init_app(app)

        # logging to stderr

        import logging

        from logging import StreamHandler

        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)

        app.logger.addHandler(file_handler)

        # handle proxy server headers

        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app)

    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))


config = dict(
    developent=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,
    heroku=HerokuConfig,
)
