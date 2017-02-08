from .persistence import Manager  # NOQA
from .mapper import Mapping  # NOQA
from . import engines  # NOQA


def database(dbapi, adapter=None, **connection_opts):
    adapter = adapter or getattr(dbapi, 'DefaultAdapter')
    return adapter(dbapi, **connection_opts)
