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

"""Classes that describe test events."""

from . import listing
from . import page
from . import helpers

from collections import OrderedDict

import abc
import datetime
import re
import urllib2

from fedfind.cached_property import cached_property

import fedfind.release

class Event(object):
    """Abstract parent class for all event classes. An event is some
    sort of test event, such as a release validation test. site must
    be an instance of wikitcms.Wiki, already with appropriate access
    rights for any actions to be performed (i.e. things instantiating
    an Event are expected to do site.login themselves if needed).
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, site):
        self.site = site


class ValidationEvent(Event):
    """A parent class for different types of release validation event.
    Required attributes: version, shortver, category_page.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, site, release, milestone='', compose='', date=''):
        super(ValidationEvent, self).__init__(site)
        self.release = release
        self.milestone = milestone
        self.compose = compose
        self.date = date
        self.parent_category_page = listing.TcmsCategory(site, release)
        self.download_page = page.DownloadPage(self.site, self)

    @abc.abstractproperty
    def ff_release(self):
        """Should return a fedfind Release object that matches this
        ValidationEvent. Should probably be a cached_property.
        """
        pass

    @abc.abstractproperty
    def valid_pages(self):
        """A list of the expected possible result pages (as
        page.ValidationPage objects) for this test event, derived from
        the available test types and the naming convention.
        """
        pass

    @abc.abstractproperty
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """
        pass

    @property
    def result_pages(self):
        """A list of wikitcms page objects for currently-existing
        pages that are a part of this test event, according to the
        naming convention.
        """
        pages = self.site.allresults(
            prefix="Fedora {0} ".format(self.version))
        return [p for p in pages if isinstance(p, page.ValidationPage)]

    @property
    def summary_page(self):
        """The page.SummaryPage object for the event's result summary
        page. Very simple property, but not set in __init__ as the
        summary page object does (slow) wiki roundtrips in  __init__.
        """
        return page.SummaryPage(self.site, self)

    @property
    def sortname(self):
        """A string that will sort correctly when compared against the
        same property of other ValidationEvents (and ValidationPages).
        """
        return helpers.fedora_release_sort(self.version)

    @property
    def has_bootiso(self):
        """Does at least one boot.iso exist for this compose?"""
        query = fedfind.release.Query('imagetype', ('boot',))
        if self.ff_release.find_images(queries=[query]):
            return True
        else:
            return False

    @property
    def compose_exists(self):
        """Does the compose for this event seem to exist at all?"""
        return self.ff_release.exists

    @property
    def image_table(self):
        """A nicely formatted download table for the images for this
        compose. Here be dragons (and wiki table syntax). What you get
        from this is a table with one row for each unique 'image
        identifier' - the payload plus the image type - and columns
        for all arches in the entire image set; if there's an image
        for the given image type and arch then there'll be a download
        link in the appropriate column.
        """
        # Start by iterating over all images and grouping them by load
        # (that's imagedict) and keeping a record of each arch we
        # encounter (that's arches).
        arches = set()
        imagedict = dict()
        for img in self.ff_release.all_images:
            imgid = '{0} {1}'.format(img.payload, img.imagetype)
            if img.arch:
                arches.add(img.arch)
            # The dict values are lists of images. We could use a
            # DefaultDict here, but faking it is easy too.
            if imgid in imagedict:
                imagedict[imgid].append(img)
            else:
                imagedict[imgid] = [img]
        # Now we have our data, sort the dict using the weight from
        # fedfind...for our purposes we can just
        # use the weight of the first image.
        imagedict = OrderedDict(sorted(imagedict.items(),
                                       key=lambda x: x[1][0].weight,
                                       reverse=True))
        # ...and sort the arches (just so they don't move around in
        # each new page and confuse people).
        arches = sorted(arches)

        # Now generate the table.
        table = '{| class="wikitable sortable collapsible" width=100%\n|-\n'
        # Start of the header row...
        table += '! Image'
        for arch in arches:
            # Add a column for each arch
            table += ' !! {0}'.format(arch)
        table += '\n'
        for (payload, imgs) in imagedict.items():
            # Add a row for each payload
            table += '|-\n'
            table += '| {0}\n'.format(payload)
            for arch in arches:
                # Add a cell for each arch (whether we have an image
                # or not)
                table += '| '
                for img in imgs:
                    if img.arch == arch:
                        # Add a link to the image if we have one
                        table += '[{0} Download]'.format(img.url)
                table += '\n'
        # Close out the table when we're done
        table += '|-\n|}'
        return table

    def update_current(self):
        """Make the CurrentFedoraCompose template on the wiki point to
        this event. The template is used for the Current (testtype)
        Test redirect pages which let testers find the current results
        pages, and for other features of wikitcms/relval. Children
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
            url = '{0}/x86_64/os/Packages/{1}/'.format(
                self.ff_release.https_url_generic, i)
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
            patt = re.compile('href="' + package + r'-(.*?)\.fc\d\d.*?\.rpm')
            match = patt.search(text)
            if match:
                ver = match.group(1)
            verdict[package] = ver
        return verdict

class ComposeEvent(ValidationEvent):
    """An Event that describes a release validation event - that is,
    the testing for a particular nightly, test compose or release
    candidate build.
    """
    def __init__(self, site, release, milestone, compose):
        self.version = "{0} {1} {2}".format(str(release), milestone, compose)
        self.shortver = "{0} {1}".format(milestone, compose)
        self.category_page = listing.TcmsCategory(site, release, milestone)
        super(ComposeEvent, self).__init__(
            site, release, milestone=milestone, compose=compose)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as
        page.ComposePage objects) for this test event, derived from
        the available test types and the naming convention.
        """
        return [page.ComposePage(self.site, self.release, t,
                                 milestone=self.milestone,
                                 compose=self.compose)
                for t in self.site.testtypes]

    @property
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """
        tmpl = ("| full = {0}\n| release = {1}\n| milestone = {2}\n"
                "| compose = {3}\n| date =\n")
        return tmpl.format(self.version, self.release, self.milestone,
                           self.compose)

    @cached_property
    def ff_release(self):
        """A fedfind release object matching this event."""
        return fedfind.release.get_release(release=self.release,
                                           milestone=self.milestone,
                                           compose=self.compose)

    @classmethod
    def from_page(cls, pageobj):
        """Return the ComposeEvent object for a given ComposePage
        object.
        """
        return cls(
            pageobj.site, pageobj.release, pageobj.milestone, pageobj.compose)


class NightlyEvent(ValidationEvent):
    """An Event that describes a release validation event - that is,
    the testing for a particular nightly, test compose or release
    candidate build. Milestone should be 'Rawhide' or 'Branched'.
    """
    def __init__(self, site, release, milestone, date):
        self.version = "{0} {1} {2}".format(str(release), milestone, date)
        self.shortver = date
        self.category_page = listing.TcmsCategory(site, release, nightly=True)
        super(NightlyEvent, self).__init__(
            site, release, milestone=milestone, date=date)

    @property
    def valid_pages(self):
        """A list of the expected possible result pages (as
        page.NightlyPage objects) for this test event, derived from
        the available test types and the naming convention.
        """
        return [page.NightlyPage(self.site, self.release, t, self.milestone,
                                 date=self.date)
                for t in self.site.testtypes]

    @property
    def _current_content(self):
        """The content for the CurrentFedoraCompose template for
        this test event.
        """
        tmpl = ("| full = {0}\n| release = {1}\n| milestone = {2}\n"
                "| compose =\n| date = {3}\n")
        return tmpl.format(
            self.version, self.release, self.milestone, self.date)

    @cached_property
    def ff_release(self):
        """A fedfind release object matching this event."""
        if self.milestone.lower() == 'rawhide':
            rel = ''
        else:
            rel = self.release
        return fedfind.release.get_release(
            release=rel, date=datetime.datetime.strptime(self.date, '%Y%m%d'))

    @classmethod
    def from_page(cls, pageobj):
        """Return the NightlyEvent object for a given NightlyPage
        object.
        """
        return cls(pageobj.site, pageobj.release, pageobj.milestone,
                   pageobj.date)
