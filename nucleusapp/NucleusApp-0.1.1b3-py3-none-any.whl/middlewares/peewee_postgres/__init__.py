import logging

from playhouse.postgres_ext import *

from ...app import SETTINGS
from ...chest import Chest
from .. import BaseMiddleware

MIDDLEWARE_POSTGRES = __name__ + '.PostgresMiddleware'
CHEST_DB = 'postgres::db'

log = logging.getLogger('NucleusApp')


class PostgresMiddleware(BaseMiddleware):
    name = 'middleware.postgres'

    def __init__(self):
        super(PostgresMiddleware, self).__init__()

        settings = Chest().root[SETTINGS]
        self.settings = settings.get('POSTGRES', {})

        active = self.settings.get('active', 'default')
        engines = self.settings.get('engines', {})
        db_config = engines.get(active, {'database': 'postgres'})
        self.db = PostgresqlExtDatabase(**db_config)

        Chest().root[CHEST_DB] = self.db
        Chest().root.lock_filed(CHEST_DB)

    def populate_module(self, appconfig):
        tables = []
        created = self.db.get_tables()
        from NucleusApp.middlewares.peewee_postgres.helper import BaseModel
        for module in appconfig.submodules.values():
            for attribute in dir(module):
                model_obj = getattr(module, attribute)
                if not isinstance(model_obj, type):
                    continue

                if issubclass(model_obj, (Model, BaseModel)) and not (model_obj in (Model, BaseModel)):
                    if model_obj not in tables and model_obj._meta.db_table not in created:
                        tables.append(model_obj)

        if tables:
            log.debug("Create new tables for '{app}': {tables}".format(
                app=appconfig.name,
                tables=[table._meta.db_table for table in tables]))
            self.db.create_tables(tables, True)
