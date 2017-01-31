# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""SqlAlchemy Model.

This model takes full advantage of the SQLAlchemy ORM and provides advanced
features when it comes to data persistence.
"""


import asyncio
import inspect
from collections import defaultdict

import sqlalchemy as sqla
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from hypr.ext import BaseModel
from hypr.globals import LocalStorage
from hypr.helpers.mini_dsl import normalize_query
from hypr.models.exc import ModelConflictException, ModelInvalidOperation


locals = LocalStorage()
Base = declarative_base()


class _ModelType(type(Base)):
    # Perform some class attribute initialization.
    def __new__(mcs, name, bases, d):
        cls = type.__new__(mcs, name, bases, d)
        return cls


class SqlAlchemyModel(Base, BaseModel, metaclass=_ModelType):
    """A model based on SQLAlchemy."""

    __abstract__ = True
    _root_session = None

    @classmethod
    def _autobind(cls):
        # automatically try to bind the SqlAlchemyModels to the database
        # declared with SQLALCHEMY_DATABASE_URL
        if cls.metadata.bind is None and locals._app is not None:
            url = locals._app.config.get('SQLALCHEMY_DATABASE_URL', None)
            if url is not None:
                cls.bind(url)

    @classmethod
    def _session(cls):
        # return the best suited SQLAlchemy session. The session are task
        # scoped when used in a request context. A teardown method is
        # registered to cleanup the session at the end of the request.

        cls._autobind()
        if cls.metadata.bind is None:
            err_msg = 'The model %s is not bound with a database.'
            raise RuntimeError(err_msg % cls.__name__)

        factory = sessionmaker(bind=cls.metadata.bind)

        try:
            session = locals.get('_sqla_localsession', None)
        except RuntimeError:
            # the session is not in a task context, use root session
            if SqlAlchemyModel._root_session is None:
                SqlAlchemyModel._root_session = scoped_session(factory)
            session = SqlAlchemyModel._root_session
        else:
            if session is None:
                session = scoped_session(factory,
                                         scopefunc=asyncio.Task.current_task)
                locals.set('_sqla_localsession', session)
            current_app = locals.app()
            current_app.register_on_request_teardown(session.close)

        return session

    @classmethod
    def bind(cls, *args, **kwargs):
        """Manually bind the SqlAlchemyModels.

        The method behaves the same way as sqlalchemy.create_engine().
        """
        cls.metadata.bind = sqla.create_engine(*args, **kwargs)

    @classmethod
    def _key(cls):
        # if the keys aren't specified, return a tuple based on the primary
        # key(s) of the model mapping
        if getattr(cls, '__key__', None) is not None:
            return super()._key()
        return tuple(c.name for c in sqla.orm.class_mapper(cls).primary_key)

    @classmethod
    def _apply_filter(cls, **kwargs):

        disjunctions = defaultdict(list)

        # reorder the query by disjunction groups and check for unknown filters
        for key, values in kwargs.items():
            for positive, value, group in values:
                disjunctions[group].append((positive, key, value))

        groups = []
        for group in disjunctions.values():     # for each disjunction group
            propositions = []
            for positive, key, value in group:  # for each proposition

                range_ = []

                attr = getattr(cls, key, None)  # TODO: handle invalid filters
                start = getattr(value, 'start', None)
                stop = getattr(value, 'stop', None)
                pattern = getattr(value, 'pattern', None)

                if pattern is not None:
                    pattern = pattern.replace('^.*', '%').replace('.*$', '%')
                    propositions.append(attr.like(pattern.strip('^$')))
                    break

                if start is not None and positive:
                    range_.append(attr >= start)
                elif start is not None:
                    range_.append(attr < start)

                if stop is not None and positive:
                    range_.append(attr < stop)
                elif stop is not None:
                    range_.append(attr >= stop)

                # if range_ is filled, this is not a direct value comparison
                # otherwise, it's a simple boolean comparison.

                if range_ and positive:
                    propositions.append(sqla.and_(*range_))
                elif range_:
                    propositions.append(sqla.or_(*range_))
                elif positive:
                    propositions.append(attr == value)
                else:
                    propositions.append(attr != value)

            groups.append(sqla.or_(*propositions))

        return cls._session().query(cls).filter(sqla.and_(*groups))

    @classmethod
    def count(cls, _search=None, **kwargs):
        """Total number of instances."""
        return cls._apply_filter(**kwargs).count()

    @classmethod
    def get(cls, _offset=0, _limit=-1, **kwargs):
        """Fetch a collection of instances matching the criterias.

        Args:
            _limit: limit the number of returned instances.
            _offset: return the instances after a given offset.

        Returns:
            A list of instances of the model.
        """
        # ensure the filters (kwargs) are in the mini query DSL format
        for k, v in kwargs.items():
            kwargs[k] = normalize_query(v)

        query = cls._apply_filter(**kwargs)

        if _limit > 0:
            return query.slice(_offset, _offset+_limit).all()
        return query.all()

    @classmethod
    def one(cls, *args):
        """Fetch an instance of the model by its key.

        Returns:
            An instance of the model.
        """
        col = cls._key()
        if len(col) != len(args):
            raise ValueError('Invalid key')

        query = cls._session().query(cls)

        # single primary key and no user-defined __key__
        if getattr(cls, '__key__', None) is None and len(col) == 1:
            return query.get(*args)

        # composite primary key
        query = query.filter_by(**dict(zip(col, args)))
        if query.count() > 1:
            msg = 'The keys does not ensure the uniqueness of an instance.'
            raise NotImplementedError(msg)
        return query.first()

    def delete(self, commit: bool=True):
        """Delete the resource from the data store.

        Args:
            commit: Perform a commit at the same time.
        """
        try:
            self._session().delete(self)
        except sqla.exc.InvalidRequestError as e:
            raise ModelInvalidOperation(str(e))
        else:
            if commit:
                self.commit()

    def save(self, commit: bool=True):
        """Make the resource persistent in the data store.

        Args:
            commit: commit inline.
        """
        self._session().add(self)
        if commit:
            self.commit()
        return self

    @classmethod
    def commit(cls):
        """Commit staged instances."""
        session = cls._session()
        try:
            session.commit()
        except sqla.exc.IntegrityError as e:
            raise ModelConflictException(str(e))

    @classmethod
    def rollback(cls):
        """Rollback pending changes."""
        cls._session().rollback()

    def __serialize__(self, context=None):
        """Serialize the instance.

        Args:
            context: change the behaviour of the serialization process.
        """
        return {k: v for k, v in inspect.getmembers(self)
                if not k.startswith('_') and not inspect.isroutine(v) and
                k != 'metadata'}    # metadata is not relevant data
