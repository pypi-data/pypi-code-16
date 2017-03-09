"""
This module defines application models
"""

import datetime
import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

import config

APP = Flask(__name__)
APP.config.from_object(os.environ['ENV_SETUP'])
DB = SQLAlchemy(APP)
BCRYPT = Bcrypt(APP)


class User(DB.Model):
    """
    Defines the structure of the users table
    """

    __tablename__ = 'users'

    id = DB.Column(DB.Integer, primary_key=True)
    first_name = DB.Column(DB.String(50), nullable=False)
    last_name = DB.Column(DB.String(50), nullable=False)
    email = DB.Column(DB.String(50), nullable=False, unique=True)
    _password = DB.Column(DB.String(255))
    date_created = DB.Column(DB.DateTime, default=datetime.datetime.now)
    date_modified = DB.Column(DB.DateTime, default=datetime.datetime.now, \
        onupdate=datetime.datetime.now)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def __repr__(self):
        return '<name %s %s>' % (self.first_name, self.last_name)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = BCRYPT.generate_password_hash(password).decode('utf-8')

    def confirm_password(self, password):
        return BCRYPT.check_password_hash(self._password, password)


class BucketList(DB.Model):
    """
    Defines the structure of the bucketlists table
    """

    __tablename__ = 'bucketlists'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False)
    created_by = DB.Column(DB.Integer, DB.ForeignKey('users.id'), nullable=False)
    items = DB.relationship('BucketListItem', \
        backref='bucketlists', \
        cascade='all, delete-orphan', \
        lazy='dynamic')
    date_created = DB.Column(DB.DateTime, default=datetime.datetime.now)
    date_modified = DB.Column(DB.DateTime, default=datetime.datetime.now, \
        onupdate=datetime.datetime.now)

    def __init__(self, name, created_by, items=[]):
        self.name = name
        self.created_by = created_by
        self.items = items

    def __repr__(self):
        return '<BucketList %s>' % (self.name)

class BucketListItem(DB.Model):
    """
    Defines the structure of a bucketlist item
    """

    __tablename__ = 'bucketlistitem'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(255), nullable=False)
    bucketlist_id = DB.Column(DB.Integer, DB.ForeignKey('bucketlists.id'))
    done = DB.Column(DB.Boolean(), default=False)
    date_created = DB.Column(DB.DateTime, default=datetime.datetime.now)
    date_modified = DB.Column(DB.DateTime, default=datetime.datetime.now, \
        onupdate=datetime.datetime.now)

    def __init__(self, name, bucketlist_id=None):
        self.name = name
        self.bucketlist_id = bucketlist_id

    def __repr__(self):
        return '<BucketList %s>' % (self.name)

DB.create_all()
