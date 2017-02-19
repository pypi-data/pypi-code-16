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

# Classes that describe different types of pages that we are interested in, and
# attributes of pages like test results and test cases, are defined in this
# file.

from . import result
from . import helpers

import re

class Page(object):
    """Parent class for all page classes. Not used directly. Child classes
    *must* define the property self.wikiname as the correct Wiki page name for
    the page.
    """

    def __init__(self, site):
        self.site = site

    @property
    def wikipage(self):
        """The page's mwclient.page object."""
        return self.site.pages[self.wikiname]

    def write(self, force=False):
        """Create a page with its default content and summary. mwclient
        exception will be raised on any page write failure.
        """
        self.site.write_page(self.wikipage, self.text,
                                   self.summary, force)

class ComposePage(Page):
    """A Page class that describes a single result page from a test compose or
    release candidate validation test event. event is the parent Event() for
    the page; compose pages are always considered to be a part of an Event.
    """

    def __init__(self, site, release, milestone, compose, testtype):
        self.release = release
        self.milestone = milestone
        self.compose = compose
        self.testtype = testtype
        if int(release) < 22:
            # We changed from 'Install' to 'Installation' at 21 Beta
            if milestone is 'Alpha' or int(release) < 21:
                self.testtype = self.testtype.replace('Installation', 'Install')
        super(ComposePage, self).__init__(site)

        # Wiki name the page should have, according to the naming convention.
        self.wikiname = ("Test Results:Fedora {release} {milestone} {compose} "
                   "{testtype}").format(
                release=release, milestone=milestone, compose=compose,
                testtype=self.testtype)
        if int(release) == 12:
            # handle slightly wacky old page names
            if milestone is 'Alpha':
                self.wikiname = self.wikiname.replace('Test Results', 'QA')
                self.wikiname = self.wikiname + " Test Results"
            if milestone is 'Final':
                self.wikiname = self.wikiname.replace(' Final', '')

        # String that will generate a clean copy of the page using the test
        # page generation template system.
        self.text = ("{{{{subst:Validation results|testtype={testtype}|"
                        "release={release}|milestone={milestone}|compose="
                        "{compose}}}}}").format(
                testtype=testtype, release=release,milestone=milestone,
                compose=compose)

        # Edit summary to be used for clean page creation.
        self.summary = ("Relval bot-created {testtype} validation results "
                           "page for {release} {milestone} {compose}").format(
                testtype=testtype, release=release,milestone=milestone,
                compose=compose)

    @property
    def results_wikitext(self):
        """Returns a string containing the wikitext for the page's results
        section. Will be None if no results are found. Relies on
        the layout for result pages remaining consistent.
        """
        pagetext = self.wikipage.edit()
        comment = re.compile('<!--.*?-->', re.S)
        pos = pagetext.find('Test Matri')
        if pos is -1:
            pos = pagetext.find('Test Areas')
        if pos is -1:
            # This string's usually at the end of the example table.
            pos = pos = pagetext.find('An unsupported test or configuration.  '
                                      'No testing is required.')
        if pos is -1:
            return None
        text = pagetext[pos:]
        text = comment.sub('', text)
        return text

    def get_resultrows(self, statuses=None, transferred=True):
        """Returns a list of result.ResultRow objects representing all the
        page's table rows containing test results.
        """
        return result.find_resultrows(self.results_wikitext, statuses,
                                       transferred)

    def update_current(self):
        """Make the Current convenience redirect page on the wiki for the
        given test type point to this page.
        """
        curr = self.site.pages['Test Results:Current ' + self.testtype
                                        + ' Test']
        self.site.write_page(curr, "#REDIRECT [[" + self.wikiname + "]]",
                                   "relval: update to current event", True)

    @property
    def sortname(self):
        """A string that will sort correctly when compared against the same
        property of other ComposePages. Use this as the key for sort functions
        to sort lists (etc) of ComposePage objects. Uses the top-level
        get_sortname() function.
        """
        n = ' '.join((str(self.release), self.milestone, self.compose,
                     self.testtype))
        return helpers.fedora_release_sort(n)

    @classmethod
    def from_wikipage(cls, wikipage):
        """Get a ComposePage object from a mediawiki Page object. This may
        seem rather roundabout, but it's useful for e.g. for getting existing
        validation pages when you don't know what composes and test types
        exist - you can get the wikipage objects from release.milestone_pages()
        and then run them through this to get wikitcms objects.

        Works by matching a regexp based on the naming convention for
        validation pages. If it thinks the wiki page name matches, it'll try
        and instantiate the ComposePage object. If that succeeds, as a further
        sanity check, it checks that the name properties match - we don't want
        you to get a ComposePage object that actually writes to a different
        wiki page than the one you based it on. If any of this fails, it
        returns None.

        Assumes that the milestone will be Alpha, Beta or Final. In practice,
        this gets the pages you want. Will match releases from 1 to 999 and
        pretty much anything for 'compose' and 'testtype'.
        """
        page_pattern = re.compile('Test[_ ]Results:Fedora[_ ](\d{1,3})'
                                  '[_ ](Alpha|Beta|Final)[_ ]([\w .]+?)'
                                  '[_ ]([\w .]+)')
        match = page_pattern.match(wikipage.name)
        if match:
            try:
                page = cls(wikipage.site, match.group(1), match.group(2),
                           match.group(3), match.group(4))
            except:
                return None
            if (page.wikiname.replace(' ', '_') !=
                wikipage.name.replace(' ', '_')):
                return None
            return page
        return None


class SummaryPage(Page):
    """A Page class that describes the result summary page for a given event.
    event is the parent Event() for the page; compose pages are always
    considered to be a part of an Event.
    """

    def __init__(self, site, event):
        super(SummaryPage, self).__init__(site)
        self.wikiname = ("Test Results:Fedora {release} {milestone} {compose} "
                         "Summary").format(
                release=event.release, milestone=event.milestone,
                compose=event.compose)
        self.summary = ("Relval bot-created validation results summary for "
                        "{release} {milestone} {compose}").format(
                release=event.release, milestone=event.milestone,
                compose=event.compose)
        self.text = "Fedora {release} {milestone} {compose}".format(
                release=event.release, milestone=event.milestone,
                compose=event.compose)
        self.text += (" [[QA:Release validation test plan|release validation]] "
                "summary. This page shows the results from all the individual "
                "result pages for this compose together. You can file results "
                "directly from this page and they will be saved into the "
                "correct individual result page.\n")
        self.text += "__TOC__"
        for testpage in event.valid_pages:
            self.text += "\n=== " + testpage.testtype + " ===\n{{"
            self.text += testpage.wikiname + "}}"

    def update_current(self):
        """Make the Current convenience redirect page on the wiki for the
        event point to this page.
        """
        curr = self.site.pages['Test Results:Current Summary']
        self.site.write_page(curr, "#REDIRECT [[" + self.wikiname + "]]",
                                   "relval: update to current event", True)


class CategoryPage(Page):
    """A Page class that describes a category for validation results. A release
    version must be passed. If rawhide is True, will be a Rawhide nightly
    testing result category for that release. Otherwise, if a milestone is
    passed, will be a category for results for that milestone for that release.
    If no milestone is passed, will be the top-level category for results for
    that release.
    """

    def __init__(self, site, release, milestone=None, rawhide=False):
        super(CategoryPage, self).__init__(site)
        if rawhide is True:
            self.wikiname = ("Category:Fedora {release} Rawhide Test "
                             "Results").format(release=release)
            ## TODO complete this
        elif milestone:
            self.wikiname = ("Category:Fedora {release} {milestone} "
                             "Test Results").format(release=release,
                                                    milestone=milestone)
            self.text = ("{{{{Validation results milestone category|release="
                         "{release}|milestone={milestone}}}}}").format(
                    release=release, milestone=milestone)
            self.summary = ("Relval bot-created validation result category page"
                        " for Fedora {release} {milestone}").format(
                    release=release, milestone=milestone)
        else:
            self.wikiname = ("Category:Fedora {release} Test Results").format(
                    release=release)
            self.text = ("{{{{Validation results milestone category|release="
                         "{release}}}}}").format(release=release)
            self.summary = ("Relval bot-created validation result category page"
                        " for Fedora {release}").format(release=release)
