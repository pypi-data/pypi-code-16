import datetime

from playhouse.postgres_ext import *

from NucleusApp.chest import Chest
from NucleusApp.middlewares.peewee_postgres import CHEST_DB


def db():
    return Chest().root[CHEST_DB]


def _db_table_func(model: object):
    name = ''
    for pos, symbol in enumerate(model.__name__):
        name += '_' + symbol if symbol.isupper() and pos > 1 else symbol
    return name.lower()


class BaseModel(Model):
    created_date = DateTimeTZField(default=None, null=True)
    modified_date = DateTimeTZField(default=None, null=True)

    def save(self, force_insert=False, only=None):
        if self.created_date is None:
            date = datetime.datetime.now()
            self.created_date = date
            self.modified_date = date
        else:
            self.modified_date = datetime.datetime.now()
        super(BaseModel, self).save(force_insert, only)

    class Meta:
        database = db()
        db_table_func = _db_table_func
