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
    result_pattern = re.compile(r'{{result.+?}}')
    oldres_pattern = re.compile(r'{{testresult.+?}}')
    matches = result_pattern.findall(text) + oldres_pattern.findall(text)
    for match in matches:
        results.append(Result(match))
    if statuses:
        results = [r for r in results for s in statuses if r.status and
                   s in r.status]
    if transferred is False:
        results = [r for r in results if r.transferred is False]
    return results

def find_resultrows(text, statuses=None, transferred=True):
    """Find result rows in a given chunk of wiki text. Returns a list of
    ResultRow objects. 'statuses' and 'transferred' are passed all the way
    through ResultRow to find_results() and behave as described there, for
    the Result objects in each ResultRow.
    """
    # should identify all test case names, including old ones. modern ones all
    # match QA:Testcase.*, but older ones sometimes have QA/TestCase.
    testcase_pattern = re.compile('\|.*(QA[:/]Test[^\|\]]+).*?\|', re.S)
    # row separator is |-, end of table is |}
    sep_pattern = re.compile('\|[-\}].*?\n')
    # section header - we need to distinguish between same test case and name
    # in different page sections
    section_pattern = re.compile('== *(.+?) *==')
    columns = list()
    resultrows = list()
    section = ''
    secid = 0
    rows = sep_pattern.split(text)
    for row in rows:
        rowlines = row.split('\n')
        for line in rowlines:
            # first, check if this is a column header row, and update column
            # names if so. Sometimes the header row doesn't have an explicit
            # row separator and so the 'row' might be polluted with quite a lot
            # of preceding lines, so we split the row into lines and check each
            # line in the row.
            if line.strip().find('!') == 0:
                # column titles
                columns = line.lstrip('!').split('!!')
                for column in columns:
                    # sanitize names a bit
                    newcol = column.strip()
                    try:
                        newcol = newcol.split('<ref>')[0]
                    except:
                        pass
                    try:
                        newcol = newcol.split('|')[1]
                    except:
                        pass
                    if newcol != column:
                        columns.insert(columns.index(column), newcol)
                        columns.remove(column)
        # now, check if there's a section header. if so, set 'section' to the
        # section name. 'section' will always be set to the name of the last
        # section we found. First line is a quick check to avoid use of the re
        # if there's no chance it'll match. The 'for sec in secmatches' block
        # finds the *last* match in the string (if we don't do that, we break
        # when a string contains more than one section header).
        if '==' in row:
            secmatches = section_pattern.finditer(row)
            for sec in secmatches:
                pass
            try:
                section = sec.group(1).strip().strip('=').strip().replace("'", "")
                secid += 1
            except:
                pass
        tcmatch = testcase_pattern.search(row)
        if tcmatch:
            # *may* be a result row - may also be a garbage 'row' between
            # tables which happens to contain a test case name. So we get
            # a ResultRow object but discard it if it doesn't contain any
            # results.
            resrow = ResultRow(columns, section, secid, tcmatch.group(1), row,
                               statuses, transferred)
            if resrow.results:
                resultrows.append(resrow)
    return resultrows


class Result(object):
    """A class that represents a single test result. Must be passed a string
    that is a valid single instance of the {{result}} wiki template. Parses the
    result string to provide various attributes. status should be the actual
    result (pass, fail, warn, etc), user may be a string of the user name
    lightly normalized, bugs may be a string or list of strings representing
    the bug or bug numbers. Each of these will be None if the value is not
    present in the result; status being None indicates either the literal "none"
    result status, or a malformed template string.

    transferred, if True, indicates the result is of the "previous (compose)
    run" type that is used to indicate where we think a result from a previous
    compose is valid for a later one.
    """
    def __init__(self, string):
        self.status = None
        self.user = None
        self.bugs = None
        self.transferred = False
        if "{{testresult" in string:
            self._parse_oldres(string)
        else:
            self._parse_result(string)

    def _parse_result(self, string):
        # the most complex result template you see might be:
        # {{ result | fail|adamwill | 123456|654321|615243 }}
        # we want the 'fail' and 'adamwill' bits separately, stripped and case
        # squashed (for our purposes, we don't care about the case), all the
        # bug numbers in one chunk to be parsed later to construct a list of
        # bugs, and none of the pipes, brackets, or whitespace.
        string = string.strip()
        string = string.strip('{}')
        params = string.split('|', 3)
        if len(params) < 2:
            # this is a malformed template like {{result}} or {{result foo}}
            return
        self.status = params[1].strip().lower()
        if self.status == "none":
            self.status = None
        if len(params) < 3:
            return
        self.user = params[2].strip().lower()
        if "previous " in self.user:
            self.transferred = True
        if len(params) < 4:
            return
        # result may have multiple bugs (see above), split them
        bugs = params[3].strip().split('|')
        for bug in bugs[:]:
            # sometimes people write 123456#c7, remove the suffix
            if '#' in bug:
                newbug = bug.split('#')[0]
                if unicode.isdigit(newbug):
                    bugs.remove(bug)
                    bugs.append(newbug)
                    bug = newbug
#           if not unicode.isdigit(bug):
#                   logger.debug("WARN: Unparseable bug number: %s", bug)
        self.bugs = bugs

    def _parse_oldres(self, string):
        # This was used in Fedora 12. It looks like this:
        # {{testresult/pass|FASName}}
        # Bugs were indicated with <refs>, which we're not handling for now
        string = string.strip()
        string = string.strip('{}')
        string = string.split('/')[1]
        params = string.split('|')
        if len(params) < 1:
            # this is a malformed template like {{result}} or {{result foo}}
            return
        self.status = params[0].strip().lower()
        if self.status == "none":
            self.status = None
        if len(params) < 2:
            return
        self.user = params[1].strip().lower()
        if "previous " in self.user:
            self.transferred = True

class ResultRow(object):
    """Represents a wiki table row containing results (and, implicitly, various
    other attributes). You wouldn't usually be expected to instantiate this
    yourself; result.find_resultrows() will find ResultRows in a given chunk
    of wiki text, and page.Page objects have properties representing the
    ResultRows in that page.

    It is passed a list of strings representing the column headers in the table
    where the result is found (this is used for identifying the environment of a
    given result), a string that looks like the name of a test case
    (find_resultrows decides whether a wiki table row is a "result row" based on
    whether it contains the name of a test case), and a string for the wiki
    text.

    name starts out being the same as testcase, but may be changed to the link
    text used in the test case column during parsing; this is for the 'two
    dimensional' result tables which have many rows that represent a second
    set of 'environments' for a test case. For such rows you can find both the
    actual test case and the 'name', depending on what you need.

    boxes is the number of cells that may contain results (we expect blank
    result cells to contain '{{result|none}}'). milestone is the earliest
    milestone for which the test must be completed, as indicated in the table
    (currently, we assume that if a table has a 'Milestone' column, it will be
    the first one) - for very old pages, this may be 'Tier1', 'Tier2', 'Tier3'
    rather than 'Alpha', 'Beta', 'Final'. results is a dict of lists of Result
    objects, keyed by the 'environment' of the results - that is, the title of
    the column in which they appear. Cells can contain more than one result,
    hence the list (it is always a list, even if it contains only one result).
    """
    def __init__(self, columns, section, secid, testcase, row, statuses=None,
                 transferred=True):
        self.columns = columns
        self.section = section
        self.secid = secid
        self.testcase = testcase
        self.name = testcase
        self.boxes = 0
        self.milestone = None
        self.results = dict()
        self._parse_row(row, statuses, transferred)

    def _parse_row(self, row, statuses, transferred):
        result_pattern = re.compile(r'{{result.+?}}')
        oldres_pattern = re.compile(r'{{testresult.+?}}')
        # this is slightly presumptuous, but holds up for every result page
        # I've tested so far; it's possible there may be some with whitespace
        cells = row.split('\n|')
        for ms in ('Alpha', 'Beta', 'Final', 'Optional', 'Tier1', 'Tier2',
                    'Tier3'):
            if ms in cells[0]:
                self.milestone = ms
        for i, cell in enumerate(cells):
            if self.testcase in cell:
                try:
                    # this is where we see if we can find some link text for
                    # the test case, and assume it's the test's "name" if so
                    self.name = cell.strip().strip('[]').split('|')[1]
                    continue
                except:
                    try:
                        self.name = cell.strip().strip('[]').split()[1]
                    except:
                        continue
            res = result_pattern.search(cell)
            oldres = oldres_pattern.search(cell)
            if res or oldres:
                # any cell containing a result string is a 'result cell', and
                # the index of the cell in columns will be the title of the
                # column it is in
                self.boxes += 1
                try:
                    self.results[self.columns[i]] = find_results(cell, statuses,
                                                                 transferred)
                except:
                    # FIXME: debug (messy table, see e.g. F15 'Multi Image')
                    pass
