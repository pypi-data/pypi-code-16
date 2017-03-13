# -*- coding: utf-8 -*-

import random
from sqlalchemy.orm import Session
from sqlalchemy.util import safe_reraise


# ref: http://techspot.zzzeek.org/2012/01/11/django-style-database-routers-in-sqlalchemy/  # noqa
class RoutingSession(Session):
    """Routing session based on binding name
    """
    _name = None

    def __init__(self, engines, *args, **kwargs):
        super(RoutingSession, self).__init__(*args, **kwargs)
        self.engines = engines
        self.slaves = [e for r, e in engines.items() if r != 'master']
        if not self.slaves:
            self.slaves = engines

    def get_bind(self, mapper=None, clause=None):
        if self._name:
            return self.engines[self._name]
        elif self._flushing:
            return self.engines['master']
        else:
            return random.choice(self.slaves)

    def using_bind(self, name):
        s = RoutingSession(self.engines)
        vars(s).update(vars(self))
        s._name = name
        return s

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.transaction is None:
            return
        try:
            if exc_type is None:
                try:
                    self.commit()
                except:
                    with safe_reraise():
                        self.rollback()
            else:
                self.rollback()
        finally:
            self.close()
