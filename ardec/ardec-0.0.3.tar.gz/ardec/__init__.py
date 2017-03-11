"""
ActiveRecord-style decorators

Wrap functions in decorators to log output like an ActiveRecord migration.
"""

import sys
from datetime import datetime
try:
    from contextlib import ContextDecorator
except ImportError:
    from contextlib2 import ContextDecorator

__version__ = '0.0.3'


# pylint: disable=invalid-name
class migration(ContextDecorator):
    """ Decorator for migrations. """
    def __init__(self, name=None):
        self.name = name or type(self).__name__
        self.start = self.label = None

    def __enter__(self):
        self.start = datetime.utcnow()
        self.label = self.start.strftime("%Y%m%d%H%M%S")
        self.log(
            "== {} {} "
            .format(self.label, self.name)
            .ljust(79, "=") + "\n")
        return self

    def __exit__(self, *exc):
        self.log(
            "== {} {} ({}s) "
            .format(self.label, self.name, self.delta())
            .ljust(79, "=") + "\n\n")
        return False

    def delta(self):
        """ Helper to get time delta. """
        start = self.start or datetime.utcnow()
        return round((datetime.utcnow() - start).total_seconds(), 4)

    @staticmethod
    def log(msg):
        """ Write message to stdout & flush. """
        sys.stdout.write(msg)
        sys.stdout.flush()


# pylint: disable=invalid-name,too-few-public-methods
class stage(migration):
    """ Decorator for migration stages. """
    def __enter__(self):
        self.start = datetime.utcnow()
        self.log("-- {}\n".format(self.name))
        return self

    def __exit__(self, *exc):
        self.log("   -> {}s\n".format(self.delta()))
        return False
