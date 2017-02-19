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

from . import result as rs
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

    @property
    def sections(self):
        """A list of the page's sections. Each section is represented
        by a dict whose values provide various attributes of the
        section.
        """
        return self.site.api('parse', page=self.wikiname,
                         prop='sections')['parse']['sections']

    def write(self, force=False):
        """Create a page with its default content and summary. mwclient
        exception will be raised on any page write failure.
        """
        self.site.write_page(self.wikipage, self.text,
                                   self.summary, force)


class ComposePage(Page):
    """A Page class that describes a single result page from a test compose,
    release candidate or nightly validation test event.
    """

    def __init__(self, site, release, testtype, milestone="", compose="",
                 date="", rawhide=""):
        self.release = release
        self.testtype = testtype
        if int(release) < 22:
            # We changed from 'Install' to 'Installation' at 21 Beta
            if milestone is 'Alpha' or int(release) < 21:
                self.testtype = self.testtype.replace('Installation', 'Install')
        self.milestone = milestone
        self.compose = compose
        self.date = date
        if date:
            self.version = "{} {}".format(str(release), date)
            self.shortver = date
        else:
            self.version = "{} {} {}".format(str(release), milestone, compose)
            self.shortver = "{} {}".format(milestone, compose)
        super(ComposePage, self).__init__(site)

        # Wiki name the page should have, according to the naming convention.
        self.wikiname = "Test Results:Fedora {} {}".format(self.version,
                                                           self.testtype)
        if int(release) == 12:
            # handle slightly wacky old page names
            if milestone is 'Alpha':
                self.wikiname = self.wikiname.replace('Test Results', 'QA')
                self.wikiname = self.wikiname + " Test Results"
            if milestone is 'Final':
                self.wikiname = self.wikiname.replace(' Final', '')

        # String that will generate a clean copy of the page using the test
        # page generation template system.
        self.text = ("{{{{subst:Validation results|testtype={}|release={}"
                        "|milestone={}|compose={}|date={}"
                        "|rawhide={}}}}}").format(
                testtype, release, milestone, compose, date, rawhide)

        # Edit summary to be used for clean page creation.
        self.summary = ("Relval bot-created {} validation results page for "
                           "{}").format(testtype, self.version)

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

    @property
    def results_sections(self):
        """A list of the sections in the page which (most likely)
        contain test results. Takes all the sections in the page,
        finds the one one which looks like the first "test results"
        section and returns that section and those that follow it - or
        returns all sections after the Key section, if it can't find
        one which looks like the first results section.
        """
        secs = self.sections
        for i, sec in enumerate(secs):
            if 'Test Matri' in sec['line'] or 'Test Areas' in sec['line']:
                first = i
                break
            elif 'Key' in sec['line']:
                first = i+1
        return secs[first:]

    @property
    def sortname(self):
        """A string that will sort correctly when compared against the same
        property of other ComposePages. Use this as the key for sort functions
        to sort lists (etc) of ComposePage objects. Uses the top-level
        get_sortname() function.
        """
        n = ' '.join((self.version, self.testtype))
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
        compose_pattern = re.compile('Test[_ ]Results:Fedora[_ ](\d{1,3})'
                                     '[_ ](Alpha|Beta|Final)[_ ]([\w .]+?)'
                                     '[_ ]([\w .]+)')
        cmatch = compose_pattern.match(wikipage.name)
        if cmatch:
            try:
                page = cls(wikipage.site, cmatch.group(1), cmatch.group(4),
                           milestone=cmatch.group(2), compose=cmatch.group(3))
            except:
                return None
        else:
            nightly_pattern = re.compile('Test[_ ]Results:Fedora[_ ](\d{1,3})'
                                         '[_ ](\d{8,8})[_ ]([\w .]+)')
            nmatch = nightly_pattern.match(wikipage.name)
            if nmatch:
                try:
                    page = cls(wikipage.site, nmatch.group(1), nmatch.group(3),
                               date=nmatch.group(2))
                except:
                    return None
        if page:
            if (page.wikiname.replace(' ', '_') !=
                wikipage.name.replace(' ', '_')):
                return None
            return page
        return None

    def get_resultrows(self, statuses=None, transferred=True):
        """Returns the result.ResultRow objects representing all the
        page's table rows containing test results. Each ResultRow
        object is the third element of a 3-tuple, with the first two
        being the normalized name and the numeric index of the section
        in which it was found on the page.
        """
        sections = self.results_sections
        rows = list()
        pagetext = self.wikipage.edit()
        for i, sec in enumerate(sections):
            try:
                nextsec = sections[i+1]
            except:
                nextsec = None
            section = sec['line']
            secid = sec['index']
            if nextsec:
                sectext = pagetext[sec['byteoffset']:nextsec['byteoffset']]
            else:
                sectext = pagetext[sec['byteoffset']:]
            newrows = rs.find_resultrows(sectext, section, secid, statuses,
                                      transferred)
            rows.extend(newrows)
        return rows

    def update_current(self):
        """Make the Current convenience redirect page on the wiki for the
        given test type point to this page.
        """
        curr = self.site.pages['Test Results:Current ' + self.testtype
                                        + ' Test']
        self.site.write_page(curr, "#REDIRECT [[" + self.wikiname + "]]",
                                   "relval: update to current event", True)

    def add_result(self, result, row, env):
        """Adds a result to the page. Must be passed a Result(), the
        result.ResultRow() object representing the row into which a
        result will be added, and the name of the environment for which
        the result is to be reported. Works by replacing the first
        instance of the row's text encountered in the page or page
        section. Expected to be used together with get_resultrows,
        which provides the ResultRow() objects.
        """
        none = rs.Result()
        nonetext = none.result_template
        restext = result.result_template
        oldsec = self.wikipage.edit(section=row.secid)
        oldrow = row.origtext
        cells = oldrow.split('\n|')
        rescell = cells[row.columns.index(env)]
        if nonetext in rescell:
            rescell = rescell.replace(nonetext, restext)
        elif '\n' in rescell:
            rescell = rescell.replace('\n', restext+'\n')
        else:
            rescell = rescell + restext
        cells[row.columns.index(env)] = rescell
        newrow = '\n|'.join(cells)
        newsec = oldsec.replace(oldrow, newrow, 1)
        summary = ("Result for test: {} environment: {} filed "
                   "via relval").format(row.name, env)
        self.site.write_page(self.wikipage, newsec, summary, section=row.secid,
                             force=True)


class SummaryPage(Page):
    """A Page class that describes the result summary page for a given event.
    event is the parent Event() for the page; summary pages are always
    considered to be a part of an Event.
    """

    def __init__(self, site, event):
        super(SummaryPage, self).__init__(site)
        if event.date:
            version = "{} {}".format(event.release, event.date)
        else:
            version = "{} {} {}".format(
                event.release, event.milestone, event.compose)
        self.wikiname = "Test Results:Fedora {} Summary".format(version)
        self.summary = ("Relval bot-created validation results summary for "
                        "{}").format(version)
        self.text = ("Fedora {} [[QA:Release validation test plan|release " 
                     "validation]] summary. This page shows the results from "
                     "all the individual result pages for this compose "
                     "together. You can file results directly from this page "
                     "and they will be saved into the correct individual "
                     "result page.\n").format(version)
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
    version must be passed. If nightly is True, will be a nightly testing
    result category for that release. Otherwise, if a milestone is passed,
    will be a category for results for that milestone for that release.
    If no milestone is passed, will be the top-level category for results for
    that release.
    """

    def __init__(self, site, release, milestone=None, nightly=False):
        super(CategoryPage, self).__init__(site)
        if nightly is True:
            self.wikiname = ("Category:Fedora {} Nightly Test "
                             "Results").format(release)
            self.text = ("{{{{Validation results milestone category|release="
                         "{}|nightly=true}}}}").format(release)
            self.summary = ("Relval bot-created validation result category page"
                            " for Fedora {} nightly results").format(release)
        elif milestone:
            self.wikiname = "Category:Fedora {} {} Test Results".format(
                    release, milestone)
            self.text = ("{{{{Validation results milestone category|release="
                         "{}|milestone={}}}}}").format(release, milestone)
            self.summary = ("Relval bot-created validation result category page"
                            " for Fedora {} {}").format(release, milestone)
        else:
            self.wikiname = "Category:Fedora {} Test Results".format(release)
            self.text = ("{{{{Validation results milestone category|release="
                         "{}}}}}").format(release)
            self.summary = ("Relval bot-created validation result category page"
                            " for Fedora {}").format(release)
