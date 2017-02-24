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

# these are all kinda inappropriate for pytest patterns
# pylint: disable=old-style-class, no-init, protected-access, no-self-use, unused-argument

"""Tests for the helper functions."""

from __future__ import unicode_literals
from __future__ import print_function

# external imports
import uuid

# 'internal' imports
from resultsdb_conventions import helpers


class TestHelpers:
    """Tests for the helper functions."""

    def test_uuid_namespace_default(self):
        """Test the uuid_namespace helper works correctly with the
        default namespace (which should be uuid.NAMESPACE_DNS).
        """
        # this is a native 'str' in py2 and py3
        res = helpers.uuid_namespace(str('test'))
        # this is a unicode in py2, native 'str' in py3
        res2 = helpers.uuid_namespace('test')
        assert type(res) is uuid.UUID
        assert str(res) == '4be0643f-1d98-573b-97cd-ca98a65347dd'
        assert type(res2) is uuid.UUID
        assert str(res2) == '4be0643f-1d98-573b-97cd-ca98a65347dd'

    def test_uuid_unicode(self):
        """Test the uuid_namespace helper works with a name containing
        Unicode characters.
        """
        res = helpers.uuid_namespace('\u4500foobar')
        assert type(res) is uuid.UUID
        assert str(res) == 'a050b517-6677-5119-9a77-2d26bbf30507'

    def test_uuid_namespace(self):
        """Test the uuid_namespace helper works with a specified
        namespace.
        """
        ns = helpers.uuid_namespace('test')
        res = helpers.uuid_namespace('test', ns)
        assert type(res) is uuid.UUID
        assert str(res) == '18ce9adf-9d2e-57a3-9374-076282f3d95b'

# vim: set textwidth=120 ts=8 et sw=4:
