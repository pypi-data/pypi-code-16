# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Mobile Grids
"""

from __future__ import unicode_literals, absolute_import

from webhelpers.html import tags


class Grid(object):
    """
    Base class for all grids
    """
    configured = False

    def __init__(self, key, data=None, **kwargs):
        """
        Grid constructor
        """
        self.key = key
        self.data = data
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __iter__(self):
        """
        This grid supports iteration, over its data
        """
        return iter(self.data)

    def configure(self, include=None):
        """
        Configure the grid.  This must define which columns to display and in
        which order, etc.
        """
        self.configured = True

    def view_url(self, obj, mobile=False):
        route = '{}{}.view'.format('mobile.' if mobile else '', self.route_prefix)
        return self.request.route_url(route, uuid=obj.uuid)


class MobileGrid(Grid):
    """
    Base class for all mobile grids
    """

    def render_object(self, obj):
        return tags.link_to(obj, self.view_url(obj, mobile=True))
