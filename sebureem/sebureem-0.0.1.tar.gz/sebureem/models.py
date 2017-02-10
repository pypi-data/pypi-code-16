"""Models
"""
from datetime import datetime
from peewee import *
from sebureem import db

__all__ = ['Sebuks','Sebura']


class BaseModel(Model):

    class Meta:
        database = db


class Sebusik(BaseModel):
    pass


class Sebuks(BaseModel):
    name = CharField()


class Sebura(BaseModel):
    text = TextField()
    date = DateTimeField(default=datetime.now())
    topic = ForeignKeyField(Sebuks, related_name='comments')

