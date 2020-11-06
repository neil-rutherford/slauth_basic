from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import jwt
from time import time
from flask import current_app
import os
from sqlalchemy.exc import IntegrityError
from config import Config

class User(UserMixin, db.Model):
    '''
    A user is an entity that can log in and interact with the platform.

    id              : int       : Primary key.
    first_name      : str(50)   : What is the user's first name?
    last_name       : str(50)   : What is the user's surname?
    email           : str(254)  : What is the user's email address? (Used for communications and logins.)
    password_hash   : str(128)  : The hashed version of the user's password. (Note that we are not storing it in plaintext.)
    is_verified     : bool      : Has the user verified their email address?
    email_opt_in    : bool      : Does the user want to receive marketing emails?
    '''

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(254), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_verified = db.Column(db.Boolean)
    email_opt_in = db.Column(db.Boolean)

    def __repr__(self):
        '''
        Official string representation of a User object is their email address.
        '''
        return "<User {}>".format(self.email)


    def set_password(self, password):
        '''
        Hashes and stores the user's plaintext password.

        :param password:        The user's password, as a plaintext string.
        :rtype:                 Hashed version of the password is linked to the variable `password_hash`.
        '''
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        '''
        Compares a given plaintext password with the hashed password stored in the database.

        :param password:        The provided password, as a plaintext string.
        :rtype:                 Boolean.
        '''
        return check_password_hash(self.password_hash, password)


    def get_reset_password(self, expires_in=600):
        '''
        Generates a password reset token. Used for part 1 of password reset process.

        :param expires_in:      In seconds, how much time do we have before the token expires? (Default 600 seconds.)
        :rtype:                 Encoded JSON Web Token (JWT), as a string.
        '''
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, Config.SECRET_KEY, algorithm='HS256').decode('utf-8')
    

    def get_verify_email(self, expires_in=600):
        '''
        Generates a email verification token. Used for part 2 email verification process.

        :param expires_in:      In seconds, how much time do we have before the token expires? (Default 600 seconds.)
        :rtype:                 Encoded JSON Web Token (JWT), as a string.
        '''
        return jwt.encode({'verify_email': self.email, 'exp': time() + expires_in}, Config.SECRET_KEY, algorithm='HS256').decode('utf-8')


    @staticmethod
    def verify_reset_password_token(token):
        '''
        Decodes a password reset token. Used for part 2 of password reset proces.

        :param token:           The encoded JWT token, as a string.
        :rtype:                 User object.
        :onerror:               Returns None.
        '''
        try:
            id = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.filter_by(id=id).first()


    @staticmethod
    def verify_verify_email_token(token):
        '''
        Decodes an email verification token. Used for part 2 of email verification process.

        :param token:           The encoded JWT token, as a string.
        :rtype:                 User object.
        :onerror:               Returns None.
        '''
        try:
            email = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])['verify_email']
        except:
            return
        return User.query.filter_by(email=email).first()


    @staticmethod
    def create(**kwargs):
        '''
        Creates a new user object.

        :param **kwargs:        Keyword arguments necessary to create the user.
        :rtype:                 User object
        :onerror:               If there is an integrity error, the database is rolled back to its previous error-free state.
        '''
        user = User(**kwargs)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return user


@login.user_loader
def load_user(id):
    '''
    Callback for reloading a user from the session. (Necessary for Flask-Login to function.)

    :param id:      The user primary key, as an integer.
    :rtype:         User object
    :onerror:       Returns None if the user does not exist.
    '''
    return User.query.get(int(id))