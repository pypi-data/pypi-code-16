"""Sebureem

Sebureem is a comment server similar to Discuss.
Is purpose is to allow add easily comment sections to web pages.

Sebureem is powered by Bottle for the webserver and use Peewee ORM and SQLite 
for handling data persistence.

"Sebureem" is the Kotava word for "comments" or "group of comments

"""
from flask import Flask
from peewee import SqliteDatabase

__version__ = "0.1.0"

db = SqliteDatabase("test.db")

app = Flask(__name__)

from .app import serve


