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

import fedfind.helpers
import re
from mwclient import errors as mwe
from mwclient import page as mwp

class Page(mwp.Page):
    """Parent class for all page classes. Can be instantiated directly
    if you just want to take advantage of the convenience methods like
    sections() and save(). Available attributes: seedtext, summary.
    Note 'name' is defined by mwp.Page's __init__.
    """

    def __init__(self, site, wikiname, info=None, extra_properties={}):
        super(Page, self).__init__(site, wikiname, info, extra_properties)
        # Used for sanity check by the page generator
        self.checkname = wikiname

    @property
    def sections(self):
        """A list of the page's sections. Each section is represented
        by a dict whose values provide various attributes of the
        section. Returns an empty list for non-existent page (or any
        other API error).
        """
        try:
            apiout = self.site.api('parse', page=self.name, prop='sections')
        except mwe.APIError:
            return []
        return apiout['parse']['sections']

    def write(self, createonly=True):
        """Create a page with its default content and summary. mwclient
        exception will be raised on any page write failure.
        """
        self.save(self.seedtext, self.summary, createonly=createonly)

    def save(self, *args, **kwargs):
        """Same as the original, but handle Fedora's captcha system.
        If you've already retrieved the current text, you can pass it
        in as oldtext, and we will check to see if oldtext and text
        are the same. If they are, we return a dict with the key
        nochange set to an empty string - this saves a needless extra
        remote roundtrip."""
        if 'oldtext' in kwargs and args[0] == kwargs['oldtext']:
            return dict(nochange='')
        try:
            ret = super(Page, self).save(*args, **kwargs)
        except mwe.EditError as err:
            # Handle captchas. The captcha plugin used on the Fedora
            # wiki helpfully gives us the question we have to answer..
            question = err.args[1]['captcha']['question']
            # ...but just for fun, with a unicode "minus" symbol.
            question = question.replace(u'\u2212', u'-')
            captchaid = err.args[1]['captcha']['id']
            if question:
                answer = eval(question)
                ret = super(Page, self).save(*args, captchaword=answer,
                                             captchaid=captchaid, **kwargs)
            else:
                raise
        return ret


class ValidationPage(Page):
    """A parent class for different types of release validation event
    pages, containing common properties and methods. Required
    attributes: version, shortver, seedtext.
    """
    def __init__(self, site, release, testtype, milestone='', compose='',
                 info=None):
        self.release = release
        self.milestone = str(milestone)
        try:
            self.compose = fedfind.helpers.date_check(
                compose, fail_raise=True, out='str')
        except ValueError:
            self.compose = str(compose)
        self.version = "{0} {1} {2}".format(
            self.release, self.milestone, self.compose)
        self.testtype = str(testtype).capitalize()

        # Wiki name the page should have, according to the naming
        # convention.
        wikiname = "Test Results:Fedora {0} {1}".format(self.version,
                                                        self.testtype)
        super(ValidationPage, self).__init__(site, wikiname, info)

        # Edit summary to be used for clean page creation.
        self.summary = ("Relval bot-created {0} validation results page for "
                        "{1}").format(testtype, self.version)

    @property
    def results_wikitext(self):
        """Returns a string containing the wikitext for the page's
        results section. Will be None if no results are found. Relies
        on the layout for result pages remaining consistent.
        """
        pagetext = self.edit().encode('utf-8')
        comment = re.compile('<!--.*?-->', re.S)
        pos = pagetext.find('Test Matri')
        if pos == -1:
            pos = pagetext.find('Test Areas')
        if pos == -1:
            # This string's usually at the end of the example table.
            pos = pagetext.find("An unsupported test or configuration. No "
                                "testing is required.")
        if pos == -1:
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
        if not secs:
            # empty page or some other malarkey
            return secs
        first = None
        for i, sec in enumerate(secs):
            if 'Test Matri' in sec['line'] or 'Test Areas' in sec['line']:
                first = i
                break
            elif 'Key' in sec['line']:
                first = i+1
        return secs[first:]

    @property
    def sortname(self):
        """A string that will sort correctly when compared against the
        same property of other ValidationPages. Use this as the key
        for sort functions to sort lists (etc) of ComposePage objects.
        Uses the top-level get_sortname() function.
        """
        n = ' '.join((self.version, self.testtype))
        return helpers.fedora_release_sort(n)

    def get_resultrows(self, statuses=None, transferred=True):
        """Returns the result.ResultRow objects representing all the
        page's table rows containing test results. Each ResultRow
        object is the third element of a 3-tuple, with the first two
        being the normalized name and the numeric index of the section
        in which it was found on the page.
        """
        sections = self.results_sections
        if not sections:
            return list()
        rows = list()
        pagetext = self.edit().encode('utf-8')
        comment = re.compile('<!--.*?-->', re.S)
        for i, sec in enumerate(sections):
            try:
                nextsec = sections[i+1]
            except:
                nextsec = None
            section = sec['line'].encode('utf-8')
            secid = sec['index'].encode('utf-8')
            if nextsec:
                sectext = pagetext[sec['byteoffset']:nextsec['byteoffset']]
            else:
                sectext = pagetext[sec['byteoffset']:]
            # strip comments
            sectext = comment.sub('', sectext)
            newrows = rs.find_resultrows(sectext, section, secid, statuses,
                                         transferred)
            rows.extend(newrows)
        return rows

    def update_current(self):
        """Make the Current convenience redirect page on the wiki for
        the given test type point to this page.
        """
        curr = self.site.pages[
            'Test Results:Current {0} Test'.format(self.testtype)]
        curr.save("#REDIRECT [[{0}]]".format(self.name),
                  "relval: update to current event", createonly=None)

    def add_result(self, result, row, env):
        """Adds a result to the page. Must be passed a Result(), the
        result.ResultRow() object representing the row into which a
        result will be added, and the name of the environment for
        which the result is to be reported. Works by replacing the
        first instance of the row's text encountered in the page or
        page section. Expected to be used together with get_resultrows
        which provides the ResultRow() objects.
        """
        none = rs.Result()
        nonetext = none.result_template
        restext = result.result_template
        oldsec = self.edit(section=row.secid).encode('utf-8')
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
        summary = ("Result for test: {0} environment: {1} filed "
                   "via relval").format(row.name, env)
        self.save(newsec, summary, section=row.secid, createonly=None)


class ComposePage(ValidationPage):
    """A Page class that describes a single result page from a test
    compose or release candidate validation test event.
    """
    def __init__(self, site, release, testtype, milestone, compose, info=None):
        super(ComposePage, self).__init__(
            site, release=release, milestone=milestone, compose=compose,
            testtype=testtype, info=info)
        self.shortver = "{0} {1}".format(self.milestone, self.compose)

        # String that will generate a clean copy of the page using the
        # test page generation template system.
        self.seedtext = ("{{{{subst:Validation results|testtype={0}"
                         "|release={1}|milestone={2}|compose={3}}}}}").format(
            testtype, self.release, self.milestone, self.compose)


class NightlyPage(ValidationPage):
    """A Page class that describes a single result page from a nightly
    validation test event.
    """
    def __init__(self, site, release, testtype, milestone, compose, info=None):
        super(NightlyPage, self).__init__(
            site, release=release, milestone=milestone, compose=compose,
            testtype=testtype, info=info)
        self.shortver = self.compose

        # String that will generate a clean copy of the page using the
        # test page generation template system.
        self.seedtext = ("{{{{subst:Validation results|testtype={0}"
                         "|release={1}|milestone={2}|date={3}}}}}").format(
            testtype, self.release, self.milestone, self.compose)


class SummaryPage(Page):
    """A Page class that describes the result summary page for a given
    event. event is the parent Event() for the page; summary pages are
    always considered to be a part of an Event.
    """
    def __init__(self, site, event, info=None):
        wikiname = "Test Results:Fedora {0} Summary".format(event.version)
        super(SummaryPage, self).__init__(site, wikiname, info)
        self.summary = ("Relval bot-created validation results summary for "
                        "{0}").format(event.version)
        self.seedtext = (
            "Fedora {0} [[QA:Release validation test plan|release "
            "validation]] summary. This page shows the results from all the "
            "individual result pages for this compose together. You can file "
            "results directly from this page and they will be saved into the "
            "correct individual result page.\n").format(event.version)
        self.seedtext += "__TOC__"
        for testpage in event.valid_pages:
            self.seedtext += "\n=== " + testpage.testtype + " ===\n{{"
            self.seedtext += testpage.name + "}}"

    def update_current(self):
        """Make the Current convenience redirect page on the wiki for the
        event point to this page.
        """
        curr = self.site.pages['Test Results:Current Summary']
        curr.save("#REDIRECT [[{0}]]".format(self.name),
                  "relval: update to current event", createonly=None)


class DownloadPage(Page):
    """The page containing image download links for a ValidationEvent.
    As with SummaryPage, is always associated with a specific event.
    """
    def __init__(self, site, event, info=None):
        wikiname = "Template:Fedora {0} Download".format(event.version)
        self.summary = "Relval bot-created download page for {0}".format(
            event.version)
        super(DownloadPage, self).__init__(site, wikiname, info)
        self.event = event

    @property
    def seedtext(self):
        """Implemented as a property because it requires fedfind
        round trips.
        """
        return self.event.image_table

    def update_current(self):
        """Kind of a hack - relval needs this to exist as things
        stand. I'll probably refactor it later.
        """
        pass


class TestDayPage(Page):
    """A Test Day results page. Usually contains table(s) with test
    cases as the column headers and users as the rows - each row is
    one user's results for all of the test cases in the table. Note
    this class is somewhat incomplete and really can only be used
    for its own methods, do *not* try writing one of these to the
    wiki.
    """

    def __init__(self, site, date, subject, info=None):
        wikiname = "Test Day:{0} {1}".format(date, subject)
        super(TestDayPage, self).__init__(site, wikiname, info)
        self.date = date
        self.subject = subject

    def fix_app_results(self):
        """The test day app does its own bug references outside the
        result template, instead of including them as the final
        parameters to the template like it should. This fixes that, in
        a fairly rough and ready way.
        """
        badres = re.compile('({{result.*?)}} {0,2}'
                            '(<ref>{{bz\|\d{6,7}}}</ref>) ?'
                            '(<ref>{{bz\|\d{6,7}}}</ref>)? ?'
                            '(<ref>{{bz\|\d{6,7}}}</ref>)? ?'
                            '(<ref>{{bz\|\d{6,7}}}</ref>)? ?'
                            '(<ref>{{bz\|\d{6,7}}}</ref>)? ?'
                            '(<ref>{{bz\|\d{6,7}}}</ref>)?')
        text = oldtext = self.edit()
        oldtext = text
        matches = badres.finditer(text)
        for match in matches:
            bugs = list()
            groups = match.groups()
            for group in groups[1:]:
                if group:
                    bugs.append(group[10:-8])
            text = text.replace(match.group(0),
                                match.group(1) + '||' + '|'.join(bugs) + '}}')
        return self.save(text, summary=u"Fix testday app-generated results to "
                         "use {{result}} template for bug references",
                         oldtext=oldtext)

    def long_refs(self):
        """People tend to include giant essays as <ref> notes on test
        day results, which really makes table rendering ugly when
        they're dumped in the last column of the table. This finds all
        <ref> notes over 150 characters long, moves them to the "long"
        group, and adds a section at the end of the page with all the
        "long" notes in it. The 'end of page discovery' is a bit
        hacky, it just finds the last empty line in the page except
        for trailing lines and sticks the section there, but that's
        usually what we want - basically we want to make sure it
        appears just above the category memberships at the bottom of
        the page. It does go wrong *sometimes*, so good idea to check
        the page after it's edited.
        """
        text = oldtext = self.edit()
        if '<ref group="long">' in text:
            # Don't run if we've already been run on this page
            return dict(nochange='')
        refpatt = re.compile('<ref>(.+?</ref>)', re.S)
        matches = refpatt.finditer(text)
        found = False
        for match in matches:
            if len(match.group(0)) > 150:
                found = True
                text = text.replace(match.group(0),
                                    u'<ref group="long">' + match.group(1))
        if found:
            text = helpers.rreplace(
                text.strip(), '\n\n',
                '\n\n== Long comments ==\n<references group="long" />\n\n', 1)
            return self.save(text, summary=u"Move long comments to a separate "
                             "section at end of page", oldtext=oldtext)
        else:
            # If we didn't find any long refs, don't do anything
            return dict(nochange='')
