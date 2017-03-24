# maildrake/config.py
# Part of Mail Drake, an email server for development and testing.
#
# Copyright © 2017 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Application configuration for Mail Drake. """

import collections
import importlib
import os.path
import types


ServerAddress = collections.namedtuple('ServerAddress', ['host', 'port'])


project_root_path = os.path.dirname(__file__)

options = types.SimpleNamespace(
        DATABASE_NAME="maildrake",
        DATABASE_DIR=project_root_path,
        DATABASE_SCHEMA=os.path.join(
            project_root_path, "store", "schema.sql"),
        DEBUG=True,
        SECRET_KEY="3ad5112b3db390d46c293fb65a8571fb0ba4579d",
        USERNAME="admin",
        PASSPHRASE="admin",
        )


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
