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

import re
import sys

def find_results(text, statuses=None, transferred=True):
    """Find test results in a given chunk of wiki text. Returns a list of
    Result objects. If statuses is not None, it should be something that
    provides strings when iterated, and only result objects whose status
    matches one of the given statuses will be returned. If transferred is
    False, results like {{result|something|previous TC5 run}} will not be
    returned.
    """
    results = list()
    # identifies an instance of the result template.
    # will break if the result contains another template, but don't do that.
    # the lookahead is used to capture the 'comments' for the result: we
    # keep matching up until we hit the next instance of the template, or
    # the end of the current line ($). The re.M is vital or this breaks.
    result_pattern = re.compile(r'{{result.+?}}.*?(?={{result|$)', re.M)
    oldres_pattern = re.compile(r'{{testresult.+?}}.*?(?={{testresult|$)', re.M)
    for res in result_pattern.findall(text):
        results.append(Result.from_result_template(res))
    for oldres in oldres_pattern.findall(text):
        results.append(Result.from_testresult_template(oldres))
    if statuses:
        results = [r for r in results for s in statuses if r.status and
                   s in r.status]
    if transferred is False:
        results = [r for r in results if r.transferred is False]
    return results

def find_resultrows(text, section='', secid=0, statuses=None, transferred=True):
    """Find result rows in a given chunk of wiki text. Returns a list of
    ResultRow objects. 'statuses' and 'transferred' are passed all the way
    through ResultRow to find_results() and behave as described there, for
    the Result objects in each ResultRow.
    """
    # should identify all test case names, including old ones. modern ones all
    # match QA:Testcase.*, but older ones sometimes have QA/TestCase.
    testcase_pattern = re.compile(r'(QA[:/]Test.+?)[\|\]\n]')
    # row separator is |-, end of table is |}
    sep_pattern = re.compile('\|[-\}].*?\n')
    columns = list()
    resultrows = list()
    rows = sep_pattern.split(text)
    for row in rows:
        rowlines = row.split('\n')
        for line in rowlines:
            # first, check if this is a column header row, and update column
            # names if so. Sometimes the header row doesn't have an explicit
            # row separator and so the 'row' might be polluted with quite a lot
            # of preceding lines, so we split the row into lines and check each
            # line in the row.
            line = line.strip()
            if line.find('!') == 0 and line.find('!!') > 0:
                # column titles. this is slightly incorrect: mw syntax allows
                # for '! title\n! title\n! title' as well as '! title !! title
                # !! title'. But we don't seem to use that syntax anywhere.
                columns = line.lstrip('!').split('!!')
                for column in columns:
                    # sanitize names a bit
                    newcol = column.strip()
                    newcol = newcol.strip("'[]")
                    newcol = newcol.strip()
                    try:
                        # drop out any <ref> block
                        p1 = newcol.index("<ref>")
                        p2 = newcol.index("</ref>") + 6 # length
                        newcol = newcol[:p1] + newcol[p2:]
                        newcol = newcol.strip()
                    except:
                        pass
                    try:
                        newcol = newcol.split('|')[1]
                    except:
                        pass
                    if newcol != column:
                        columns.insert(columns.index(column), newcol)
                        columns.remove(column)
        tcmatch = testcase_pattern.search(row)
        if tcmatch:
            # *may* be a result row - may also be a garbage 'row' between
            # tables which happens to contain a test case name. So we get
            # a ResultRow object but discard it if it doesn't contain any
            # result cells. This test works even if the actual results are
            # filtered by statuses= or Transferred=, because the resrow.
            # results dict will always have a key for each result column,
            # though its value may be an empty list.
            resrow = ResultRow.from_wiki_row(tcmatch.group(1), columns, row,
                                             section, secid, statuses,
                                             transferred)
            if resrow.results:
                resultrows.append(resrow)
    return resultrows


class Result(object):
    """A class that represents a single test result. Note that a 'none'
    result, as you get if you just instantiate this class without
    arguments, is a thing, at least for wikitcms; when text with
    {{result|none}} templates in it is parsed, such objects may be
    created/returned, and you can produce the {{result|none}} text as
    the result_template property of such an instance.

    You would usually instantiate this class directly to report a new
    result.

    Methods that parse existing results will use one of the class
    methods that returns a Result() with the appropriate attributes.
    When one of those parsers produces an instance it will set the
    attribute origtext to record the exact string parsed to produce the
    instance.

    transferred, if True, indicates the result is of the "previous
    (compose) run" type that is used to indicate where we think a
    result from a previous compose is valid for a later one.
    """
    def __init__(self, status=None, user=None, bugs=None, comment=''):
        self.status = status
        self.user = user
        self.bugs = bugs
        if self.bugs:
            self.bugs = [str(bug) for bug in self.bugs]
        self.comment = comment
        self.transferred = False

    def __str__(self):
        if not self.status:
            return "Result placeholder - {{result|none}}"
        status = 'Result: ' + self.status.capitalize()
        if self.transferred:
            user = ' transferred: ' + self.user
        elif self.user:
            user = ' from ' + self.user
        else:
            user = ''
        if self.bugs:
            bugs = ', bugs: ' + ', '.join(self.bugs)
        else:
            bugs = ''
        if self.comment:
            comment = ', comment: ' + self.comment
            comment = comment.replace('<ref>', '')
            comment = comment.replace('</ref>', '')
        else:
            comment = ''
        return status + user + bugs + comment

    @property
    def result_template(self):
        """The {{result}} template string that would represent the
        properties of this result in a wiki page.
        """
        bugtext = ''
        commtext = self.comment
        usertext = ''
        if self.status is None:
            status = 'none'
        else:
            status = self.status
        if self.bugs:
            bugtext = "|" + '|'.join(self.bugs)
        if self.user:
            usertext = "|" + self.user
        tmpl = "{{{{result|{status}{usertext}{bugtext}}}}}{commtext}".format(
                status=status, usertext=usertext, bugtext=bugtext,
                commtext=commtext)
        return tmpl

    @classmethod
    def from_result_template(cls, string):
        """Returns a Result object based on the {{result}} template.
        The most complex result template you see might be:
        {{ result | fail|adamwill | 123456|654321|615243 }} comment
        We want the 'fail' and 'adamwill' bits separately and stripped,
        and all the bug numbers in one chunk to be parsed later to
        construct a list of bugs, and none of the pipes, brackets, or
        whitespace. We record the comment exactly as is.
        """
        template, comment = string.strip().split('}}', 1)
        comment = comment.strip()
        template = template.lstrip('{')
        params = template.split('|', 3)
        # Pad the non-existent parameters to make things cleaner later
        while len(params) < 4:
            params.append('')

        for i, param in enumerate(params):
            params[i] = param.strip()
            if params[i] == '':
                params[i] = None
        status, user, bugs = params[1:]
        if status and status.lower() == "none":
            status = None

        if bugs:
            bugs = [b.strip() for b in bugs.split('|') if b.strip() != ""]
            for i, bug in enumerate(bugs):
                # sometimes people write 123456#c7, remove the suffix
                if '#' in bug:
                    newbug = bug.split('#')[0]
                    if newbug.isdigit():
                        bugs[i] = newbug

        res = cls(status, user, bugs, comment)
        res.origtext = string
        if user and "previous " in user:
            res.transferred = True
        return res

    @classmethod
    def from_testresult_template(cls, string):
        '''Returns a Result object based on the {{testresult}} template.
        This was used in Fedora 12. It looks like this:
        {{testresult/pass|FASName}} <ref>comment or bug</ref>
        The bug handling here is very special-case - it relies on the
        fact that bug IDs were always six-digit strings, at the time,
        and on the template folks used to link to bug reports - but
        should be good enough.
        '''
        bug_patt = re.compile(r'({{bz.*?(\d{6,6}).*?}})')
        emptyref_patt = re.compile(r'<ref> *?</ref>')
        template, comment = string.strip().split('}}', 1)
        template = template.lstrip('{')
        template = template.split('/')[1]
        params = template.split('|')
        try:
            status = params[0].strip().lower()
            if status == "none":
                status = None
        except:
            status = None
        try:
            user = params[1].strip().lower()
        except:
            user = None
        try:
            bugs = [b[1] for b in bug_patt.findall(comment)]
        except:
            bugs = None
        if comment:
            comment = bug_patt.sub('', comment)
            comment = emptyref_patt.sub('', comment)
            if comment.replace(' ', '') == '':
                comment = ''
        else:
            pass
        res = cls(status, user, bugs, comment)
        res.origtext = string
        if user and "previous " in user:
            res.transferred = True
        return res

    @classmethod
    def from_qatracker(cls, result):
        '''Converts a result object from the QA Tracker library to a
        wikitcms-style Result. Returns a Result instance with origres
        as an extra property that is a pointer to the qatracker result
        object.
        '''
        if result.result == 1:
            status = 'pass'
        elif result.result == 0:
            status = 'fail'
        else:
            status = None
        if result.reportername:
            user = result.reportername
        else:
            user = None
        if result.comment:
            comment = result.comment
        else:
            comment = ''
        # This produces an empty string if there are no bugs, a dict
        # if there are bugs
        bugs = eval(result.bugs)
        if bugs:
            bugs = bugs.keys()
        else:
            bugs = None
        res = cls(status, user, bugs, comment)
        res.origres = result
        return res

class TestInstance(object):
    """Represents the broad concept of a 'test instance': that is, in
    any test management system, the 'basic unit' of a single test for
    which some results are expected to be reported. In 'Wiki TCMS', for
    instance, this corresponds to a single row in a results table, and
    that is what the ResultRow() subclass represents. A subclass for
    QATracker would represent a single test in a build of a product.

    The 'testcase' is the basic identifier of a test instance. It will
    not necessarily be unique, though - in any test management system
    you may find multiple test instances for the same test case (in
    different builds and different products). The concept of the 'name'
    derives from Wiki TCMS, where it is not uncommon for a set of
    test instances to have the same 'testcase' but a different 'name',
    which in that system is the link text: there will a column which
    for each row contains [[testcase|name]], the testcase being the
    same but the name being different. The concept doesn't seem
    entirely specific to Wiki TCMS, though, so it's represented here.
    Commonly the 'testcase' and 'name' will be the same, when each
    instance within a set has a different 'testcase' the name should
    be identical to the testcase.

    milestone is, roughly, the priority of the test: milestone is
    slightly Fedora-specific language, a hangover from early wikitcms
    versions which didn't consider other systems. For Fedora it will be
    Alpha, Beta or Final, usually. For Ubuntu it may be 'mandatory',
    'optional' or possibly 'disabled'.

    results is required to be a dict of lists; the dict keys represent
    the test's environments. If the test system does not have the
    concept of environments, the dict can have a single key with some
    sort of generic name (like 'Results'). The values must be lists of
    instances of wikitcms.Result or a subclass of it.
    """
    def __init__(self, testcase, milestone='', results=dict()):
        self.testcase = testcase
        self.name = testcase
        self.milestone = milestone
        self.results = results


class ResultRow(TestInstance):
    """Represents the 'test instance' concept for Wiki TCMS, where it
    is a result row from the tables used to contain results. Some
    Wiki TCMS-specific properties are encoded here. columns is the list
    of columns in the table in which the result was found (this is
    needed to figure out the environments for the results, as the envs
    are represented by table columns, and to know which cell to edit
    when modifying results). origtext is the text which was parsed to
    produce the instance, if it was produced by the from_wiki_row()
    class method which parses wiki text to produce instances. section
    and secid are the wiki page section in which the table from which
    the row came is located; though these are in a way attributes of
    the page, this is really another case where an MW attribute is
    just a way of encoding information about a *test*. The splitting
    of result pages into sections is a way of sub-grouping tests within
    each page. So it's appropriate to store those attributes here.

    At present you typically get ResultRow instances by calling a
    ComposePage's get_resultrows() method, which runs its text through
    result.find_resultrows(), which isolates the result rows in the
    wiki text and runs through through this class' from_wiki_row()
    method. This will always provide instances with a full set of
    the above-described attributes.
    """
    def __init__(self, testcase, columns, section='', secid=None, milestone='',
                 origtext='', results=dict()):
        super(ResultRow, self).__init__(testcase, milestone, results)
        self.columns = columns
        self.origtext = origtext
        self.section = section
        self.secid = secid

    # From https://stackoverflow.com/questions/390250 , useful
    # equality behaviour.
    def __eq__(self, other):
        """Equality for ResultRows: if all identifying characteristics
        and the origtext match. __dict__ match is too strong as the
        'results' attribute is a list of Result instances; each time
        you instantiate the same ResultRow you get different Result
        objects."""
        if isinstance(other, self.__class__):
            ours = (self.testcase, self.name, self.secid, self.origtext)
            theirs = (other.testcase, other.name, other.secid, other.origtext)
            return ours == theirs
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test."""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    @classmethod
    def from_wiki_row(cls, testcase, columns, text, section, secid,
                      statuses=None, transferred=True):
        results = dict()
        # this is slightly presumptuous, but holds up for every result page
        # I've tested so far; it's possible there may be some with whitespace,
        # and '| cell || cell || cell' is permitted as an alternative to
        # '| cell\n| cell\n| cell' but we do not seem to use it.
        cells = text.split('\n|')
        milestone = ''
        for ms in ('Alpha', 'Beta', 'Final', 'Optional', 'Tier1', 'Tier2',
                    'Tier3'):
            if ms in cells[0]:
                milestone = ms
        for i, cell in enumerate(cells):
            if testcase in cell:
                try:
                    # this is where we see if we can find some link text for
                    # the test case, and assume it's the test's "name" if so
                    altname = cell.strip().strip('[]').split('|')[1]
                    continue
                except:
                    try:
                        altname = cell.strip().strip('[]').split()[1]
                    except:
                        altname = None
            if '{{result' in cell or '{{testresult' in cell:
                # any cell containing a result string is a 'result cell', and
                # the index of the cell in columns will be the title of the
                # column it is in. find_results() returns an empty list if
                # all results are filtered out, so the results dict's keys will
                # always represent the full set of environments for this test.
                try:
                    results[columns[i]] = find_results(cell, statuses,
                                                       transferred)
                except:
                    # FIXME: log (messy table, see e.g. F15 'Multi Image')
                    pass
        row = cls(testcase, columns, section, secid, milestone, text, results)
        if altname:
            row.name = altname
        return row


class TrackerBuildTest(TestInstance):
    """Represents a 'result instance' from QA Tracker: this is the data
    associated with a single testcase in a single build.
    """
    def __init__(self, tcname, tcid, milestone='', results=dict()):
        super(TrackerBuildTest, self).__init__(tcname, milestone, results)
        self.tcid = tcid

    @classmethod
    def from_api(cls, testcase, build):
        results = dict()
        results['Results'] = list()
        tcname = testcase.title
        tcid = testcase.id
        milestone = testcase.status_string
        for res in build.get_results(testcase):
            results['Results'].append(Result.from_qatracker(res))
        return cls(tcname, tcid, milestone, results)
