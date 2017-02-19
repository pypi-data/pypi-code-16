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

from . import page as pg
from . import event as ev
from . import listing as li

import mwclient
import re

class Wiki(mwclient.Site):
    """Extends the mwclient.Site class with some extra capabilities."""
    # parent class has a whole bunch of args, so just pass whatever through.
    # always init this the same as a regular mwclient.Site instance.
    def __init__(self, *args, **kwargs):
        super(Wiki, self).__init__(*args, **kwargs)
        # override the 'pages' property so it returns wikitcms Pages when
        # appropriate
        self.pages = li.TcmsPageList(self)

    @property
    def current_compose(self):
        """A dict of the key / value pairs from the CurrentFedora
        Compose page which is the canonical definition of the 'current'
        primary arch validation testing compose. You can usually expect
        keys full, release, date, milestone, and compose. The page is
        normally written by ValidationEvent.update_current().
        """
        currdict = dict()
        valpatt = re.compile('^\| *?(\w+?) *?= *([\w .]*?) *$', re.M)
        page = self.pages['Template:CurrentFedoraCompose']
        for match in valpatt.finditer(page.edit()):
            currdict[match.group(1)] = match.group(2)
        return currdict

    @property
    def matrices(self):
        """A list of dicts representing pages in the test matrix
        template category. These are the canonical definition of
        'existing' test types. Done this way - rather than using the
        category object's ability to act as an iterator over its member
        page objects - because this method respects the sort order of
        the member pages, whereas the other does not. The sort order is
        used in creating the overview summary page.
        """
        category = self.pages['Category:QA test matrix templates']
        return category.members(generator=False)

    @property
    def testtypes(self):
        """Test types, derived from the matrix page names according to
        a naming convention. A list of strings.
        """
        return [m['title'].replace(u'Template:', u'')
                .replace(u' test matrix', u'').encode('utf-8')
                 for m in self.matrices]

    def add_to_category(self, page_name, category_name, summary=''):
        """Add a given page to a given category if it is not already a
        member. Takes strings for the names of the page and the
        category, not mwclient objects.
        """
        page = self.pages[page_name]
        text = page.edit().encode('utf-8')
        if category_name not in text:
            text += "\n[[{0}]]".format(category_name)
            page.save(text, summary, createonly=False)

    def walk_category(self, category):
        """Simple recursive category walk. Returns a list of page
        objects that are members of the parent category or its
        sub-categories, to any level of recursion. 14 is the Category:
        namespace.
        """
        pages = dict()
        for page in category:
            if page.namespace == 14:
                sub_pages = self.walk_category(page)
                for sub_page in sub_pages:
                    pages[sub_page.name] = sub_page
            else:
                pages[page.name] = page
        pages = pages.values()
        return pages

    def allresults(self, prefix=None, start=None, redirects='all'):
        """A generator for pages in the Test Results: namespace,
        similar to mwclient's allpages, allcategories etc. generators.
        This is a TcmsPageList, so it returns wikitcms objects when
        appropriate. Note, if passing prefix or start, leave out the
        "Test Results:" part of the name.
        """
        gen = li.TcmsPageList(self, prefix=prefix, start=start, namespace=116,
                           redirects=redirects)
        return gen
