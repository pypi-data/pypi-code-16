import logging

import flask
from raven.contrib.flask import Sentry


class SepiidaSentry(Sentry):
    def get_user_info(self, request):
        return flask.g.current_user

def add_sentry_support(application, sentry_dsn):
    raven = SepiidaSentry(application, dsn=sentry_dsn, logging=True, level=logging.ERROR)
    application.config.setdefault('RAVEN', raven)
    logging.getLogger('webargs.flaskparser').setLevel(logging.CRITICAL)
