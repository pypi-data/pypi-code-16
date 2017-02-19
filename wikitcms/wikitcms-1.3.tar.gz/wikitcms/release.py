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

from . import page

class Release(object):
    """Class for a Fedora release. site is an mwclient site object. Release
    is a string containing a Fedora release version (e.g. 21).
    """

    def __init__(self, release, wiki):
        self.release = release
        self.category_name = ("Category:Fedora {release} Test Results").format(
                release=self.release)
        self.site = wiki

    @property
    def rawhide_pages(self):
        return self.site.allpages(prefix="Fedora {release} Rawhide".format(
                release=self.release), namespace='116')

    def milestone_pages(self, milestone=None):
        category = page.CategoryPage(self.site, self.release, milestone)
        catpage = category.wikipage
        pages = self.site.walk_category(catpage)
        return pages

    def category_pages(self):
            return self.site.walk_category(self.site.pages[self.category_name])
