#
# Flask-NextCaller
#
# Copyright (C) 2017 Boris Raicheff
# All rights reserved
#


import logging

from pynextcaller.client import NextCallerClient


logger = logging.getLogger('Flask-NextCaller')


class NextCaller(object):
    """
    Flask-NextCaller

    Documentation:
    https://flask-nextcaller.readthedocs.io

    API:
    https://nextcaller.com/documentation

    :param app: Flask app to initialize with. Defaults to `None`
    """

    client = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        username = app.config.get('NEXTCALLER_API_USERNAME')
        password = app.config.get('NEXTCALLER_API_PASSWORD')
        if username is None or password is None:
            logger.warning('NEXTCALLER_USERNAME or NEXTCALLER_PASSWORD not set')
            return
        self.client = NextCallerClient(username, password, sandbox=app.debug)

    def __getattr__(self, name):
        return getattr(self.client, name)


# EOF
