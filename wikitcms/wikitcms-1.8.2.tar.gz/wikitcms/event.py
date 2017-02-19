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

from . import listing
from . import page
from . import helpers

import re
import urllib2

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


class ValidationEvent(Event):
    """A parent class for different types of release validation event.
    Child classes must define self.imageurl as a public URL for the
    directory containing .treeinfo.
    """
    def __init__(self, site, release):
        super(ValidationEvent, self).__init__(site)
        self.release = release
        self.parent_category_page = listing.TcmsCategory(site, release)

    @property
    def result_pages(self):
        """A list of wikitcms page objects for currently-existing pages that
        are a part of this test event, according to the naming convention.
        """
        pages = self.site.allresults(
                prefix="Fedora {0} ".format(self.version))
        return [p for p in pages if isinstance(p, page.ValidationPage)]

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

    @property
    def has_bootiso(self):
        """Is there a boot.iso in the tree for this compose?"""
        url = '{0}images/boot.iso'.format(self.imageurl)
        try:
            urllib2.urlopen(url)
            return True
        except:
            return False

    @property
    def compose_exists(self):
        """Does the compose for this event seem to exist at all?"""
        try:
            urllib2.urlopen(self.imageurl)
            return True
        except:
            return False

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
        curr.save(content, "relval: update to current event", createonly=None)

    def get_package_versions(self, packages):
        """Passed a list of package names, returns a dict with the
        names as the keys and the versions of those packages found in
        the compose's tree as the values. May raise an exception if
        the compose doesn't exist, or it can't reach the server.
        """
        verdict = dict()
        initials = set([p[0].lower() for p in packages])
        text = ''
        # Grab the directory indexes we need
        for i in initials:
            url = '{0}Packages/{1}/'.format(self.imageurl, i)
            index = urllib2.urlopen(url)
            text += index.read()
        # Now find each package's version. This is making a couple of
        # assumptions about how the index HTML source will look and
        # also assuming that the 'package version' is the bit after
        # packagename- and before .fcXX, it's not perfect (won't give
        # epochs and won't work for non-fcXX dist'ed packages, for
        # e.g.) but should be good enough.
        for package in packages:
            ver = ''
            patt = re.compile('href="' + package + '-(.*?)\.fc\d\d.*?\.rpm')
            match = patt.search(text)
            if match:
                ver = match.group(1)
            verdict[package] = ver
        return verdict

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
        self.category_page=listing.TcmsCategory(site, release, milestone)
        if milestone == 'Final':
            path = "{0}_{1}".format(str(release), compose)
        else:
            path = self.version.replace(' ', '_')
        self.imageurl = ('http://dl.fedoraproject.org/pub/alt/stage/{0}/Server'
                         '/x86_64/os/').format(path)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as page.ComposePage
        objects) for this test event, derived from the available test types and
        the naming convention.
        """
        return [page.ComposePage(self.site, self.release, t,
                                  milestone=self.milestone,
                                  compose=self.compose)
                 for t in self.site.testtypes]

    @property
    def _current_content(self):
        tmpl = ("| full = {0}\n| release = {1}\n| milestone = {2}\n"
                "| compose = {3}\n| date =\n")
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

    def __init__(self, site, release, tree, date):
        super(NightlyEvent, self).__init__(site, release)
        self.date = date
        self.tree = tree
        self.version = "{0} {1} {2}".format(str(release), tree, date)
        self.shortver = date
        self.category_page = listing.TcmsCategory(site, release, nightly=True)
        if tree == 'Rawhide':
            self.imageurl = ('http://kojipkgs.fedoraproject.org/mash/rawhide-'
                             '{0}/rawhide/x86_64/os/').format(date)
        else:
            self.imageurl = ('http://kojipkgs.fedoraproject.org/mash/branched-'
                             '{0}/{1}/x86_64/os/').format(date, release)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as page.ComposePage
        objects) for this test event, derived from the available test types and
        the naming convention.
        """
        return [page.NightlyPage(self.site, self.release, t, self.tree,
                                  date=self.date)
                 for t in self.site.testtypes]

    @property
    def _current_content(self):
        tmpl = ("| full = {0}\n| release = {1}\n| milestone = {2}\n"
                "| compose =\n| date = {3}\n")
        return tmpl.format(self.version, self.release, self.tree,
                            self.date)

    @classmethod
    def from_page(cls, page):
        """Return the NightlyEvent object for a given NightlyPage object."""
        return cls(page.site, page.release, page.tree, page.date)
