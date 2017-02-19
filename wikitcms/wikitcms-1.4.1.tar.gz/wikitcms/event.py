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
    wiki must be an instance of wikitcms.Wiki, already with appropriate access
    rights for any actions to be performed (i.e. things instantiating this
    class are expected to do wiki.login themselves if needed).
    """

    def __init__(self, wiki):
        self.site = wiki

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


class ComposeEvent(Event):
    """An Event that describes a release validation event - that is, the
    testing for a particular test compose or release candidate build.
    """

    def __init__(self, release, milestone, compose, wiki):
        super(ComposeEvent, self).__init__(wiki)
        self.release = release
        self.milestone = milestone
        self.compose = compose
        self.category_page = page.CategoryPage(wiki, release, milestone)
        self.parent_category_page = page.CategoryPage(wiki, release)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as page.ComposePage
        objects) for this test event, derived from the available test types and
        the naming convention.
        """
        valid_pages = [page.ComposePage(self.site, self.release,
                                        self.milestone, self.compose, x)
                       for x in self.testtypes]
        return valid_pages

    @property
    def real_pages(self):
        """A list of mwclient page objects for currently-existing pages that
        are a part of this test event, according to the naming convention.
        Namespace '116' is Test_Results.
        """
        real_pages = self.site.allpages(prefix="Fedora {release} {milestone} "
                                        "{compose} ".format(
                release=self.release, milestone=self.milestone,
                compose=self.compose), namespace='116')
        return real_pages

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
        n = ' '.join((str(self.release), self.milestone, self.compose))
        return helpers.fedora_release_sort(n)

    @classmethod
    def from_page(cls, page):
        """Return the ComposeEvent object for a given ComposePage object."""
        return cls(page.release, page.milestone, page.compose, page.wiki)

    def update_current(self):
        """Make the CurrentFedoraCompose template on the wiki point to
        this event. The template is used for the Current (testtype)
        Test redirect pages which let testers find the current results
        pages, and for other features of wikitcms/relval.
        """
        content = ' '.join((str(self.release), self.milestone, self.compose))
        content += ("<noinclude>\n{{tempdoc}}\n[[Category: Fedora Templates]]"
                    " \n</noinclude>")
        curr = self.site.pages['Template:CurrentFedoraCompose']
        self.site.write_page(curr, content, "relval: update to current event",
                             True)


class RawhideEvent(Event):
    """An Event that describes a run of the validation test suite against
    the Rawhide nightly composes for a period of time (in this case, a
    month).
    """

    def __init__(self, year, month, username=None, password=None):
        super(RawhideEvent, self).__init__(username, password)
        self.year = year
        self.month = month
