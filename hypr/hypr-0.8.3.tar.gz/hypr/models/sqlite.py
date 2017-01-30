# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""SQLite3 Model.

The SQLite3 model is a basic model for data persistence with nearly no features
nor optimizations and based on the sqlite3 module included in the standard
library of Python.

Do not use this model in production!
"""


import pickle
import sqlite3
from hypr.helpers.mini_dsl import normalize_query
from hypr.models.exc import ModelInvalidOperation, ModelConflictException
from hypr.models.base import BaseModel
from hypr.globals import LocalStorage


locals = LocalStorage()


class _ModelType(type):
    def __new__(mcs, name, bases, d):
        cls = type.__new__(mcs, name, bases, d)

        # keep a track of models with a tablename for later initialization
        if cls.__tablename__ is not None:
            SQLiteModel._known_tables.append(cls.__tablename__)
        return cls


class SQLiteModel(BaseModel, metaclass=_ModelType):
    """A model based on SQLite3.

    Supported features:
    - transactional model
    - create, read, update, delete
    - filtering, limiting and sorting of the returned instances

    The SQLiteModel does not support property mapping, querying and relational
    features of a SQL database and is not optimized. Being CPU-bound and fully
    synchronous, a request on a model with a few instances of it stored could
    result on long processing times.
    """

    _db = None
    _root_session = None
    _known_tables = []

    __key__ = 'id',
    __tablename__ = None

    @staticmethod
    def _deserialize(id, blob):
        # deserialize the blob stored in the database
        rv = pickle.loads(blob)
        setattr(rv, '_id', id)
        return rv

    @classmethod
    def _autobind(cls):
        # automatically try to bind the model to the database declared in Hypr
        # configuration "MODELS_SQLITE_DATABASE_URI"
        if SQLiteModel._db is None and locals._app is not None:
            url = locals._app.config.get('MODELS_SQLITE_DATABASE_URI', None)
            if url is not None:
                SQLiteModel.bind(url)

    @classmethod
    def _session(cls):
        # return a session.
        cls._autobind()
        if SQLiteModel._db is None:
            raise RuntimeError('SQLiteModel is not bound to a database.')

        try:
            session = locals.get('_sqlite_localsession', None)
        except RuntimeError:
            if SQLiteModel._root_session is None:
                SQLiteModel._root_session = sqlite3.connect(
                    SQLiteModel._db, uri=True, isolation_level='DEFERRED')
            session = SQLiteModel._root_session
        else:
            if session is None:
                session = sqlite3.connect(
                    SQLiteModel._db, uri=True, isolation_level='DEFERRED')
                locals.set('_sqlite_localsession', session)
            current_app = locals.app()
            current_app.register_on_request_teardown(session.close)

        return session

    @classmethod
    def bind(cls, url):
        """Bind the models to a database."""
        SQLiteModel._db = url

    @classmethod
    def create_all(cls):
        """Create all required tables."""
        session = cls._session()
        q = 'CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY, obj BLOB)'

        for tablename in cls._known_tables:
            session.execute(q % tablename)
        session.commit()

    @property
    def id(self):
        """The resource id."""
        return getattr(self, '_id', None)

    @classmethod
    def get(cls, _offset=0, _limit=-1, _sort=None, **kwargs):
        """Get a list of instances."""
        if _sort is None:
            _sort = ()
        elif not isinstance(_sort, tuple):
            _sort = _sort,

        # Ensure the filters (kwargs) are in the HMQ format.
        for k, v in kwargs.items():
            kwargs[k] = normalize_query(v, key=k)

        # get all instances
        c = cls._session().cursor()
        query = 'SELECT id, obj FROM %s' % cls.__tablename__
        instances = (cls._deserialize(*i) for i in c.execute(query))

        # filter by using the default _match() method. Complexity is O(n) !
        instances = [i for i in instances if i._match(**kwargs)]

        # apply sorting
        # the sort arguments order is reversed to reproduce the behaviour of
        # SQL (ORDER BY A, B === sort by A then by B for each value of A).
        for string in reversed(_sort):
            reverse = string[0] == '-'
            key = string[reverse:]
            instances.sort(key=lambda i: getattr(i, key), reverse=reverse)

        # pagination
        if _limit > 0:
            return instances[_offset:_offset + _limit]

        return instances

    @classmethod
    def one(cls, *args):
        """Get one resource."""
        rv = None

        if cls.__key__ == ('id',):  # tiny optimization to limit damages.
            msg = 'The keys does not ensure the uniqueness of an instance.'
            query = 'SELECT id, obj FROM %s WHERE id = ?' % cls.__tablename__

            c = cls._session().cursor()
            for row in c.execute(query, args):
                if rv is not None:  # pragma: no cover
                    # this shouldn't happen if id is the table's primary key
                    raise NotImplementedError(msg)
                rv = cls._deserialize(*row)
        else:
            rv = super().one(*args)  # use default unoptimized version.
        return rv

    def save(self, commit=True):
        """Make the instance persistent in the data store.

        Args:
            commit: Perform a commit at the same time.
        """
        obj = pickle.dumps(self)
        c = self._session().cursor()

        if self.id is None:
            query = 'INSERT INTO %s (obj) VALUES (?)'
            c.execute(query % self.__tablename__, (obj,))
        else:
            query = 'UPDATE %s SET obj = ? WHERE id = ?'
            c.execute(query % self.__tablename__, (obj, self.id))
            if c.rowcount == 0:
                raise ModelConflictException('instance not found')

        self._id = c.lastrowid or self.id
        if commit:
            self.commit()

        return self

    def delete(self, commit=True):
        """Delete the instance from the data store.

        Args:
            commit: Perform a commit at the same time.
        """
        if self.id is None:
            raise ModelInvalidOperation('instance not persistent')

        query = 'DELETE FROM %s WHERE id = ?'

        c = self._session().cursor()
        c.execute(query % self.__tablename__, (self.id,))
        if c.rowcount == 0:
            raise ModelConflictException('instance not found')

        if commit:
            self.commit()

        return self

    @classmethod
    def commit(cls):
        """Commit changes."""
        cls._session().commit()

    @classmethod
    def rollback(cls):
        """Rollback changes."""
        cls._session().rollback()
