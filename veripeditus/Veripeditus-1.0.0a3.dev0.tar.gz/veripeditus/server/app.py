"""
Flask application code for the Veripeditus server

This module contains everything to set up the Flask application.
"""

# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016  Dominik George <nik@naturalnet.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version, with the Game Cartridge Exception.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# pragma pylint: disable=wrong-import-position
# pragma pylint: disable=unused-import

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from osmalchemy import OSMAlchemy

DB = SQLAlchemy()
OA = OSMAlchemy(DB)

def create_app():
    # Get a basic Flask application
    app = Flask(__name__)

    # Default configuration
    # FIXME allow modification after module import
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['BASIC_REALM'] = "Veripeditus"
    app.config['OSMALCHEMY_ONLINE'] = True
    app.config['ENABLE_CODE_EDITOR'] = False
    app.config['CODE_EDITOR_PATH'] = '/var/lib/veripeditus/editor'

    # Load configuration from a list of text files
    cfglist = ['/var/lib/veripeditus/dbconfig.cfg', '/etc/veripeditus/server.cfg']
    for cfg in cfglist:
        app.config.from_pyfile(cfg, silent=True)

    DB.init_app(app)
    DB.app = app

    # Import model and create tables
    import veripeditus.server.model
    import veripeditus.framework.model
    DB.create_all()

    # Run initialisation code
    from veripeditus.server.control import init
    init(app)

    # Set up REST API
    from veripeditus.server.rest import init_rest
    api_manager = init_rest(app)
    OA.create_api(api_manager)

    return app
