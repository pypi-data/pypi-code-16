#!/usr/bin/env python
# -*-encoding:utf-8-*-

from importlib import import_module
from sqlalchemy.orm import sessionmaker


class Connection(object):
    def __init__(self, conn_str=None):
        if not conn_str:
            conn_str = 'postgresql://psql:*@*/psqldb'
        self.engine = create_engine(conn_str, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # def create(self):
    #     metadata = MetaData()
    #     metadata.create_all(self.engine)

    def create_by_metadata(self, module_str, meta_str='metadata'):
        module = import_module(module_str)
        metadata = getattr(module, meta_str)
        metadata.create_all(self.engine)

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()


if __name__ == '__main__':
    conn = Connection(None)
    # conn.create()
    conn.create_by_metadata('models', 'metadata')
