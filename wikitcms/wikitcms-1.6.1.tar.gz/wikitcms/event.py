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

# Classes that describe test events are defined in this file.

from . import page
from . import helpers

class Event(object):
    """Parent class for all event classes. Not expected to be used directly.
    Rather use one of the classes that inherits from this, like ComposeEvent.
    An event is some sort of test event, such as a release validation test.
    site must be an instance of wikitcms.Wiki, already with appropriate access
    rights for any actions to be performed (i.e. things instantiating this
    class are expected to do site.login themselves if needed).
    """

    def __init__(self, site):
        self.site = site

    @property
    def matrices(self):
        """A list of dictionaries representing pages in the test matrix template
        category. These are the canonical definition of 'existing' test types.
        Done this way - rather than using the category object's ability to act
        as an iterator over its member page objects - because this method
        respects the sort order of the member pages, whereas the other does not.
        The sort order is used in creating the overview summary page.
        """
        category = self.site.pages['Category:QA test matrix templates']
        return category.members(generator=False)

    @property
    def testtypes(self):
        """Test types, derived from the matrix page names according to a naming
        convention. Returns a list of strings.
        """
        testtypes = list()
        prefix = 'Template:'
        suffix = ' test matrix'
        for matrix in self.matrices:
            matrix = matrix['title']
            matrix = matrix[len(prefix):]
            matrix = matrix[:-len(suffix)]
            testtypes.append(matrix)
        return testtypes


class ValidationEvent(Event):
    """A parent class for different types of release validation event."""
    def __init__(self, site, release):
        super(ValidationEvent, self).__init__(site)
        self.release = release
        self.parent_category_page = page.CategoryPage(site, release)

    @property
    def real_pages(self):
        """A list of mwclient page objects for currently-existing pages that
        are a part of this test event, according to the naming convention.
        Namespace '116' is Test_Results.
        """
        return self.site.allpages(prefix="Fedora {0} ".format(self.version))

    @property
    def summary_page(self):
        """The page.SummaryPage object for the event's result summary page.
        Very simple property, but not set in __init__ as the summary page
        object does (slow) wiki roundtrips in its __init__.
        """
        return page.SummaryPage(self.site, self)

    @property
    def sortname(self):
        """A string that will sort correctly when compared against the same
        property of other ComposePages. Use this as the key for sort functions
        to sort lists (etc) of ComposePage objects.
        """
        return helpers.fedora_release_sort(self.version)

    def update_current(self):
        """Make the CurrentFedoraCompose template on the wiki point to
        this event. The template is used for the Current (testtype)
        Test redirect pages which let testers find the current results
        pages, and for other features of wikitcms/relval. Child classes
        must define _current_content.
        """
        content = "{{tempdoc}}\n<onlyinclude>{{#switch: {{{1|full}}}\n"
        content += self._current_content
        content += "}}</onlyinclude>\n[[Category: Fedora Templates]]"
        curr = self.site.pages['Template:CurrentFedoraCompose']
        self.site.write_page(curr, content, "relval: update to current event",
                             True)


class ComposeEvent(ValidationEvent):
    """An Event that describes a release validation event - that is, the
    testing for a particular nightly, test compose or release candidate build.
    """

    def __init__(self, site, release, milestone, compose):
        super(ComposeEvent, self).__init__(site, release)
        self.milestone = milestone
        self.compose = compose
        self.version = "{0} {1} {2}".format(str(release), milestone, compose)
        self.shortver = "{0} {1}".format(milestone, compose)
        self.category_page=page.CategoryPage(site, release, milestone)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as page.ComposePage
        objects) for this test event, derived from the available test types and
        the naming convention.
        """
        return [page.ComposePage(self.site, self.release, t,
                                  milestone=self.milestone,
                                  compose=self.compose)
                 for t in self.testtypes]

    @property
    def _current_content(self):
        tmpl = ("| full = {0}\n| release = {1}\n| date =\n"
                "| milestone = {2}\n| compose = {3}\n| rawhide =\n")
        return tmpl.format(self.version, self.release, self.milestone,
                            self.compose)

    @classmethod
    def from_page(cls, page):
        """Return the ComposeEvent object for a given ComposePage object."""
        return cls(page.site, page.release, page.milestone, page.compose)


class NightlyEvent(ValidationEvent):
    """An Event that describes a release validation event - that is, the
    testing for a particular nightly, test compose or release candidate build.
    """

    def __init__(self, site, release, date, rawhide=False):
        super(NightlyEvent, self).__init__(site, release)
        self.date = date
        if rawhide is True:
            self.rawhide = "true"
        else:
            self.rawhide = ""
        self.version = "{0} {1}".format(str(release), date)
        self.shortver = date
        self.category_page = page.CategoryPage(site, release, nightly=True)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as page.ComposePage
        objects) for this test event, derived from the available test types and
        the naming convention.
        """
        return [page.NightlyPage(self.site, self.release, t,
                                  date=self.date, rawhide=self.rawhide)
                 for t in self.testtypes]

    @property
    def _current_content(self):
        tmpl = ("| full = {0}\n| release = {1}\n| date = {2}\n"
                "| milestone =\n| compose =\n| rawhide = {3}\n")
        return tmpl.format(self.version, self.release, self.date,
                            self.rawhide)

    @classmethod
    def from_page(cls, page):
        """Return the NightlyEvent object for a given NightlyPage object."""
        return cls(page.site, page.release, page.date, page.rawhide)
