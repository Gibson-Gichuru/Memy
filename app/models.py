from . import db
from . import login_manager

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request, url_for

from datetime import datetime


import hashlib

from markdown import markdown

import bleach


from .utils import generate_firebase_login_token


from app.exceptions import ValidationError

from .utils import firebase_login, user_uid




# call back function
@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


class DataManipulation:
    def add(self, resource):

        db.session.add(resource)

        return db.session.commit()

    def delete(self, resource):

        db.session.delete(resource)

        return db.session.commit()

    def update(self):

        return db.session.commit()


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model, DataManipulation):

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    default = db.Column(db.Boolean, default=False, index=True)

    permissions = db.Column(db.Integer)

    users = db.relationship("User", backref="role", lazy="dynamic")

    @staticmethod
    def insert_roles():

        roles = {
            "User": (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            "Moderator": (
                Permission.FOLLOW
                | Permission.COMMENT
                | Permission.WRITE_ARTICLES
                | Permission.MODERATE_COMMENTS,
                False,
            ),
            "Administrator": (0xFF, False),
        }

        for r in roles:

            role = Role.query.filter_by(name=r).first()

            if role is None:

                role = Role(name=r)

            role.permissions = roles[r][0]
            role.default = roles[r][1]

            db.session.add(role)

        db.session.commit()

    def __repr__(self):

        return "<Role {}>".format(self.name)


class Post(db.Model, DataManipulation):

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    cloud_file_name = db.Column(db.String(56), default = None)


    # relationships

    comment = db.relationship('Comment', backref="post", lazy ='dynamic')

    like = db.relationship('Like', backref='likes', lazy = 'dynamic')

    @staticmethod 
    def on_changed_body(target, value, oldvalue, initiator):

        allowed_tags = ['a', 'abbr','acronym', 'b', 'blockquote', 'code',
        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']

        target.body_html = bleach.linkify(bleach.clean(markdown(value, 
            output_format='html'), tags = allowed_tags, strip = True))


    @property
    def comments(self):

        return self.comment.order_by(Comment.timestamp.desc())


    @staticmethod
    def generate_fake(count = 100):

        from random import seed, randint
        import forgery_py

        seed()

        user_count = User.query.count()

        for i in range(count):

            u = User.query.offset(randint(0, user_count-1)).first()
            post = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,3)),
                timestamp = forgery_py.date.date(True), author = u)

            db.session.add(post)
            db.session.commit()

    @staticmethod
    def get_post_file(file_id, author_uid,author_token):

        storage = current_app.config['FIREBASE_USER_APP_INSTANCE'].storage()

        profile_path = "/data/{}/profile/{}".format(author_uid, file_id)

        return storage.child(profile_path).get_url(author_token)


    def to_json(self):

        json_post = {

            "url": url_for("api.get_post", id = self.id, _external = True),
            "body": self.body,
            "body_html":self.body_html,
            "timestamp":self.timestamp,
            "author":url_for('api.get_user', id = self.author_id, _external = True),
            "comments": url_for('api.get_post_comments', id = self.id, _external = True),
            "comment_count": self.comment.count()
        }

        return json_post


    @staticmethod
    def from_json(json_post):

        body = json_post.get('body')

        if body is None or body == '':

            raise ValidationError('post does not have a body')

        return Post(body)


class Follow(db.Model):

    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True)

    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True)

    timestamp = db.Column(db.DateTime(), default = datetime.utcnow)


class User(db.Model, DataManipulation, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(130))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default = datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
    profile_pic_id = db.Column(db.String(120), default = None)
    cover_photo_id = db.Column(db.String(120), default = None)
    firebase_user_uid = db.Column(db.String(120), default = None)
    user_uid_token = db.Column(db.String(200), default = None)

    # relationships
    posts = db.relationship('Post', backref ='author', lazy = 'dynamic')

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
        backref = db.backref('follower', lazy = 'joined'), lazy = 'dynamic',
        cascade = 'all, delete-orphan')

    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], 
        backref = db.backref('followed', lazy= 'joined'), lazy = 'dynamic',
        cascade = 'all, delete-orphan')


    comment = db.relationship('Comment', backref='author', lazy = 'dynamic')

    like = db.relationship('Like', backref='liked', lazy = 'dynamic')


    # return all the posts whose author's are the followed users by the current user instances
    @property 
    def followed_posts(self):

        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)


    # follow functionality helper functions
    @property
    def user_followers(self):

        return User.query.join(Follow, Follow.follower_id == User.id).filter(Follow.followed_id == self.id)

    @property
    def user_following(self):

        return User.query.join(Follow, Follow.followed_id == User.id).filter(Follow.follower_id == self.id)


    @property
    def firebase_custom_token(self):

        return hashlib.md5(self.email.encode('utf-8')).hexdigest()
    
    def follow(self, user):

        if not self.is_following(user):

            f = Follow(follower=self, followed =user)

            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):

        f = self.followed.filter_by(followed_id=user.id).first()

        if f:

            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):

        return  self.followed.filter_by(followed_id=user.id).first() is not None


    def is_followed_by(self, user):

        return  self.followers.filter_by(follower_id=user.id).first() is not None

    def ping(self):

        self.last_seen = datetime.utcnow()
        db.session.add(self)


    def __init__(self, **kwargs):

        super(User, self).__init__(**kwargs)

        if self.role is None:

            if self.email == current_app.config['FLASK_ADMIN']:

                self.role = Role.query.filter_by(permissions = 0xff).first()

            if self.role is None:

                self.role = Role.query.filter_by(default = True).first()


        # we want the current user to view posts from the users they are following together with their own post so
        # the current user have to follow themselves

        self.follow(self)


    def set_profile_pic(profile_pic_id):

        self.profile_pic_id = profile_pic_id


    @staticmethod
    def get_profile_pic(file_id, user_id,user_token):

        storage = current_app.config['FIREBASE_USER_APP_INSTANCE'].storage()

        profile_path = "/data/{}/profile/{}".format(user_id, file_id)

        return storage.child(profile_path).get_url(user_token)

    def can(self, permissions):

        return self.role is not None and (self.role.permissions & permissions) \
        == permissions

    def is_administrator(self):

        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):

        self.password_hash = generate_password_hash(password)


    @property
    def firebase_uid(self):

        return self.firebase_user_uid

    @firebase_uid.setter
    def firebase_uid(self, uid):

        self.firebase_user_uid = uid


    @property
    def idToken(self):

        return self.user_uid_token

    @idToken.setter
    def idToken(self, uid):

        self.user_uid_token = uid

    def verify_password(self, password):

        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):

        s = Serializer(current_app.config["SECRET_KEY"], expiration)

        return s.dumps({"confirm": self.id})

    def confirm(self, token):

        s = Serializer(current_app.config["SECRET_KEY"])

        try:

            data = s.loads(token)

        except:

            return False

        if data.get("confirm") != self.id:

            return False

        self.confirmed = True

        db.session.add(self)

        self.update()

        return True

    def generate_reset_token(self, expiration=3600):

        s = Serializer(current_app.config["SECRET_KEY"], expiration)

        return s.dumps({"reset": self.id})

    def generate_auth_token(self, expiration):

        s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)

        return s.dumps({"id":self.id})


    @staticmethod
    def verify_auth_token(token):

        s = Serializer(current_app.config['SECRET_KEY'])

        try:

            data = s.loads(token)

        except:

            return None

        return User.query.get(data['id'])


    @staticmethod
    def reset_password(token, newpassword):

        s = Serializer(current_app.config["SECRET_KEY"])

        try:

            data = s.loads(token)

        except:

            return False

        user = User.query.get(data.get("reset"))

        if user is None:

            return False

        user.password = newpassword

        db.session.add(user)

        user.update()

        return True



    # add the self following feature to all the pre-registered users on the database
    @staticmethod
    def add_self_follows():

        for user in User.query.all():

            if not user.is_following(user):

                user.follow(user)

                db.session.add(user)
                db.session.commit()


    def __repr__(self):

        return "<User {}>".format(self.username)


    def gravator(self, size = 100, default = 'identicon', rating = 'g'):

        if request.is_secure:

            url = 'https://www.gravatar.com/avatar'

        else:
            
            url = 'http://www.gravatar.com/avatar'

        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url = url, hash = hash ,size = size, default = default, rating = rating)




    @staticmethod
    def generate_fake(count = 100):

        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py


        seed()

        for i in range(count):

            u = User(email = forgery_py.internet.email_address(),
                username = forgery_py.internet.user_name(True),
                password = forgery_py.lorem_ipsum.word(),
                confirmed = True,
                name = forgery_py.name.full_name(),
                location = forgery_py.address.city(),
                about_me = forgery_py.lorem_ipsum.sentence(),
                member_since = forgery_py.date.date(True))

            db.session.add(u)

            try:

                db.session.commit()

            except IntegrityError:

                db.session.rollback()


    def to_json(self):

        json_user = {

            "url": url_for('api.get_post', id = self.id, _external = True),
            "username":self.username,
            "last_seen":self.last_seen,
            "posts": url_for('api.get_user_posts', id = self.id, _external = True),
            "followed_posts": url_for('api.get_user_followed_posts', id = self.id, _external = True),
            "followers": url_for('api.get_user_followers', id = self.id, _external = True),
            "following": url_for('api.get_user_following', id = self.id, _external = True),
            "post_count": self.posts.count(),

        }

        return json_user


    @staticmethod
    def login_users_to_firebase():

        for user in User.query.all():

            user_login = firebase_login(user.firebase_custom_token)

            user.firebase_uid = user_uid(user_login['idToken'])

            db.session.add(user)

            user.update()


    @staticmethod
    def set_user_uid_token():

        for user in User.query.all():

            user_login_to_firebase = firebase_login(user.firebase_custom_token)

            user.idToken = user_login_to_firebase['idToken']

            db.session.add(user)

            user.update()




class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod 
    def on_changed_body(target, value, oldvalue, initiator):

        allowed_tags = ['a', 'abbr','acronym','b','code','em','i','strong']

        target.body_html = bleach.linkify(bleach.clean(markdown(value, 
            output_format='html'), tags = allowed_tags, strip = True))

    def to_json(self):

        comment_json = {

            'body': self.body,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id = self.author_id, _external = True)
        }

    @staticmethod
    def from_json(comment_json):

        body = comment_json.get('body')

        if body is None or body == '':

            raise ValidationError("Comment body cannot be empty")

        return Comment(body)


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):

        return False

    def is_administrator(self):

        return False


class Like(db.Model):

    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)




login_manager.anonymous_user = AnonymousUser

###############DATABASE EVENT LISTENERS###############################
db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)