# Copyright (C) 2014 Red Hat
#
# This file is part of wikitcms.
#
# wikitcms is free software; you can redistribute it and/or modify
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

# Classes that describe distribution releases are defined in this file.

from . import page as pg
from . import listing as li

class Release(object):
    """Class for a Fedora release. site is an mwclient site object. Release
    is a string containing a Fedora release version (e.g. 21).
    """

    def __init__(self, release, wiki):
        self.release = release
        self.category_name = ("Category:Fedora {0} Test Results").format(
                self.release)
        self.site = wiki

    def milestone_pages(self, milestone=None):
        cat = li.TcmsCategory(self.site, self.release, milestone)
        pgs = self.site.walk_category(cat)
        return (p for p in pgs if isinstance(p, pg.ValidationPage))
