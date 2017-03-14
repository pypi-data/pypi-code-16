"""Contains functions regarding the db"""
from peewee import SqliteDatabase, Model, CharField, Field
from os import path
import json

db = SqliteDatabase(path.join(path.dirname(__file__), '..', 'caller', 'db.sql'))


class JSONField(Field):
    """
    Custom field which dumps and loads the value as json
    into the db. This works very well with arrays.

    """
    def db_value(self, value):
        if value is None:
            return ''
        else:
            return json.dumps(value)

    def python_value(self, value):
        if value is None:
            return ''
        else:
            return json.loads(value)


class Task(Model):
    hash = CharField()
    hostname = CharField(null=True)
    session = CharField(null=True)
    profile = CharField(null=True)
    iterations = CharField(null=True)
    dps = CharField(null=True)
    items = JSONField(null=True)

    class Meta:
        database = db


def create_tables():
    db.create_tables([Task], safe=True)

# uncomment for looging
# import logging
# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())