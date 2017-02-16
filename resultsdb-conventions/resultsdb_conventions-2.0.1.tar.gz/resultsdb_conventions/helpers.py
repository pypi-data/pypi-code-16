# Copyright (C) Red Hat Inc.
#
# resultsdb_conventions is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:   Adam Williamson <awilliam@redhat.com>

"""Miscellaneous utility functions."""

from __future__ import unicode_literals
from __future__ import print_function

# stdlib imports
import logging
import uuid

# pylint:disable=invalid-name
logger = logging.getLogger(__name__)

def uuid_namespace(name, namespace=None):
    """Create a UUID using the provided name and namespace (or default
    DNS namespace), handling string type and encoding ickiness on both
    Py2 and Py3.
    """
    # so the deal here is the passed name may be a string or a unicode
    # in Python 2 (for Python 3 we assume it's a string), and what we
    # need back is a string - not a bytestring on Python 3, or a
    # unicode on Python 2, as uuid doesn't accept either - with non-
    # ASCII characters stripped (as uuid doesn't accept those either).
    # This magic formula seems to work and produce the same UUID on
    # both.
    if not namespace:
        namespace = uuid.NAMESPACE_DNS
    return uuid.uuid5(namespace, str(name.encode('ascii', 'ignore').decode()))

# vim: set textwidth=120 ts=8 et sw=4:
