# -*- coding: utf-8 -*-

"""
takumi_sqlalchemy.database
~~~~~~~~~~~~~~~~~~~~~~~~~~

Simplify database operations by using one single object under Takumi app.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from takumi_config import config

from .routing import RoutingSession
from .utils import normalize_dsn


def _create_session(conf):
    dsn = normalize_dsn(conf['dsn'])

    def _s(x, d):
        return config.settings.get(x, d)
    max_overflow = conf.get('max_overflow', _s('DB_MAX_OVERFLOW', None))
    kwargs = {
        'pool_size': conf.get('pool_size', _s('DB_POOL_SIZE', 10)),
        'pool_recycle': conf.get('pool_recycle', _s('DB_POOL_RECYCLE', 1200))
    }
    if max_overflow is not None:
        kwargs['max_overflow'] = max_overflow

    engines = {r: create_engine(d, **kwargs) for r, d in dsn.items()}
    return scoped_session(sessionmaker(
        class_=RoutingSession,
        engines=engines,
        expire_on_commit=False
    ))


def _session_map():
    session_map = {}
    settings = config.settings['DB_SETTINGS']
    for app_name, conf in settings.items():
        session_map[app_name] = _create_session(conf)
    return session_map


class _Database(object):
    """Convenient class for representing db sessions.

    A Database instance can have multiple sessions pointed to difference
    databases.

    :Example:

    >>> db['takumi_demo'].query()
    >>> with db['takumi_demo'] as session:
    >>>...  session.query()
    """
    def __init__(self):
        self.session_map = None

    def __getitem__(self, attr):
        if self.session_map is None:
            # lazy load session map
            self.session_map = _session_map()
        return self.session_map[attr]()

    def invalidate(self):
        """Invalidate all session connections
        """
        if not self.session_map:
            return

        for session in self.session_map.values():
            if session.registry.has():
                session.registry().invalidate()
            session.remove()

db = _Database()
