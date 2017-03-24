# maildrake/web/__init__.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Web interface to Mail Drake. """

import importlib
import logging

import flask

from .. import config


logger = logging.getLogger(__package__)

store = importlib.import_module('..store', package=__package__)
config.options.DATABASE = store.sqlite.get_database_file_path()

app = flask.Flask(__name__)
app.config.from_object(config.options)

# Ensure Flask views are defined and registered to the app.
importlib.import_module('.views', package=__package__)


# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.AGPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
