# Copyright (C) 2016 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

"""The Image class, which is a kind of superset of a productmd image
dict with bonus entries and convenience methods for common operations.
"""

from __future__ import unicode_literals
from __future__ import print_function

class Image(dict):
    """An Image is a superset of a productmd image dict. It is
    initialized from a productmd image dict or a fedfind-synthesized
    facsimile of one (for composes that don't have metadata).
    """
    def __getitem__(self, key):

    def direct_url(self):
        if self.get('alt'):
            

    def _getsize(self):
        
