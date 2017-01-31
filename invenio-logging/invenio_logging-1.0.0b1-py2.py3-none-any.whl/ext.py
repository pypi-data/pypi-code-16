# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio base logging module."""

from __future__ import absolute_import, print_function

import logging


class InvenioLoggingBase(object):
    """Invenio-Logging extension for console."""

    def __init__(self, app=None):
        """Extension initialization.

        :param app: An instance of :class:`~flask.Flask`.
        """
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize app.

        :param app: An instance of :class:`~flask.Flask`.
        """

    @staticmethod
    def capture_pywarnings(handler):
        """Log python system warnings."""
        logger = logging.getLogger('py.warnings')
        # Check for previously installed handlers.
        for h in logger.handlers:
            if isinstance(h, handler.__class__):
                return
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
