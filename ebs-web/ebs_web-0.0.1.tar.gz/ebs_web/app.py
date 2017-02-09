# coding=utf-8
"""Creat a flask web application."""

from __future__ import absolute_import

import sys

from flask import Flask

from ebs_web.models import configure_engine
from ebs_web.models import init_db
from ebs_web.models import db_session

from ebs_web.api.v1 import api_v1_bp
from ebs_web.error import ApiHTTPError


def create_app(config=None):
    app = Flask(__name__,
                template_folder='ui/templates',
                static_folder='ui/static')

    app.config.from_pyfile('setting.py', silent=True)
    if config:
        app.config.from_object(config)

    if app.config['DEBUG']:
        from werkzeug.debug import DebuggedApplication
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

    # make sure that SECRET_KEY is configured.
    if not app.config['SECRET_KEY']:
        sys.stderr.write('ERROR: Secret Key is not available. '
                         'Please update your configuration.\n'
                         'To generate a key you can use openssl:\n\n'
                         '$ openssl rand -base64 32\n\n')

        sys.exit()

    # setup the database
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri and len(db_uri) > 0:
        configure_engine(db_uri)
        init_db()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # register blugprints
    configure_blueprints(app)

    # register error handler
    @app.errorhandler(ApiHTTPError)
    def handle_http_error(error):
        return error.build_response()

    if app.config['ENABLED_CROSS_DOMAIN']:
        # enable cross-domain request
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add(
                'Access-Control-Allow-Headers',
                'Content-Type,Referfer,Accept,Origin,User-Agent,X-File-Name')
            response.headers.add('Access-Control-Allow-Methods',
                                 'GET,PUT,POST,DELETE')
            return response

    # config logging
    # TODO: implement a method to config the logging
    return app


def configure_blueprints(app):
    app.register_blueprint(api_v1_bp, url_prefix=u'/api/v1')
