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

import fedfind.helpers

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
    def current_event(self):
        """The current event, as a ValidationEvent instance. Will be a
        ComposeEvent or a NightlyEvent."""
        curr = self.current_compose
        # Use of 'max' plus get_validation_event handles getting us
        # the right kind of event.
        return self.get_validation_event(
            release=curr['release'], milestone=curr['milestone'],
            compose=max(curr['date'], curr['compose']))

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

    def _check_compose(self, compose):
        """Trivial checker shared between following two methods."""
        # 'Valid' TC/RC names
        composes=set(
            '{0}{1}'.format(a, b) for a in ('TC', 'RC') for b in range(1, 21))
        if fedfind.helpers.date_check(compose, fail_raise=False):
            return 'date'
        elif str(compose).upper() in composes:
            return 'compose'
        raise ValueError("Compose must be a TC/RC identifier (TC1, RC3...) or "
                         "a date in YYYYMMDD format.")

    def _check_release_milestone(self, release, milestone):
        """If we get a string that looks like a milestone as the
        'release', turn it into the milestone and guess at the same
        release as the current validation event. This is basically to
        let us make a reasonable attempt at finding events for Rawhide
        nightly builds, which do not inherently have an associated
        release number. Raise exceptions on some nutty cases. Returns
        a (release, milestone) tuple with its best guess.
        """
        if str(release).isdigit():
            # Nothing to see here, sanitize values and return.
            return (str(release), str(milestone).capitalize())

        if not release:
            # Guess release and return.
            return (self.current_compose['release'],
                    str(milestone).capitalize())

        if any(ms == str(release).lower() for ms in ('rawhide', 'branched')):
            if milestone and str(release).lower() != str(milestone).lower():
                # This is something like 'Rawhide Branched 20150223'
                # We can't guess what the hell that means.
                raise ValueError(
                    "'release' {0} and 'milestone' {1} look like two different"
                    " milestone values. Cannot guess what is meant.".format(
                        release, milestone))
            else:
                # We have a milestone-y 'release' value and either no
                # 'compose' value or it's the same as the milestone;
                # we turn the 'release' into the milestone and guess
                # the release.
                return (self.current_compose['release'],
                        str(release).capitalize())
        # Here we have a 'release' value that isn't a digit or a
        # recognizable milestone. This isn't going to go well.
        raise ValueError("Unrecognizable 'release' value {0}".format(release))

    def get_validation_event(self, release='', milestone='', compose=''):
        """Get an appropriate ValidationEvent object for the values
        given. As with get_validation_page(), this method is for
        sloppy instantiation of pages that follow the rules. This
        method has no required arguments and tries to figure out
        what you want from what you give it. It will raise errors
        if what you give it is impossible to interpret or if it
        tries and comes up with an inconsistent-seeming result.

        If you pass a numeric release, a milestone, and a valid
        compose (TC/RC or date), it will give you the appropriate
        event, whether it exists or not. All it really does in this
        case is pick NightlyEvent or ComposeEvent for you. If you
        don't fulfill any of those conditions, it'll need to do
        some guessing/assumptions, and in some of those cases it
        will only return an Event *that actually exists*, and may
        raise exceptions if you passed a particularly pathological
        set of values.

        If you don't pass a compose argument it will get the current
        event; if you passed either of the other arguments and they
        don't match the current event, it will raise an error. It
        follows that calling this with no arguments just gives you
        current_event.

        Various other guessing heuristics are applied. In all cases,
        if you don't pass a release, the release of the current event
        will be used instead. If you pass 'Rawhide' or 'Branched' as
        the release, it will be turned into the milestone and the
        release of the current event will be used as the release.

        If you pass a date as compose with no milestone, it will see
        if there's a Rawhide nightly and return it if so, otherwise it
        will see if there's a Branched nightly and return that if so,
        otherwise raise an error. It follows that you can't get the
        page for an event that *doesn't exist yet* this way: you must
        instantiate it directly or call this method with a milestone.

        It will not attempt to guess a milestone for TC/RC composes;
        it will raise an exception in this case.

        The guessing bits require wiki roundtrips, so they will be
        slower than instantiating a class directly or using this
        method with sufficient information to avoid guessing.
        """
        try:
            (release, milestone) = self._check_release_milestone(
                release, milestone)
        except ValueError as err:
            raise ValueError("get_validation_event(): {0}".format(err[0]))
        if not compose:
            # Can't really make an educated guess without a compose,
            # so just get the current event and return it if it
            # matches any other values passed.
            event = self.current_event
            if (release and event.release != release):
                raise ValueError(
                    "get_validation_event(): Guessed event release {0} does "
                    "not match requested release {1}".format(
                        event.release, release))
            if (milestone and event.milestone != milestone):
                raise ValueError(
                    "get_validation_event(): Guessed event milestone {0} "
                    "does not match specified milestone {1}".format(
                        event.milestone, milestone))
            # all checks OK
            return event

        if self._check_compose(compose) == 'date':
            if milestone:
                return ev.NightlyEvent(
                    self, release=release, milestone=milestone,
                    compose=compose)
            else:
                # we have a date and no milestone. Try both and return
                # whichever exists. We check whether the first result
                # page has any contents so that if someone mistakenly
                # creates the wrong event, we can clean up by blanking
                # the pages, rather than by getting an admin to
                # actually *delete* them.
                rawev = ev.NightlyEvent(self, release, 'Rawhide', compose)
                pgs = rawev.result_pages
                if pgs and pgs[0].edit():
                    return rawev
                brev = ev.NightlyEvent(self, release, 'Branched', compose)
                pgs = brev.result_pages
                if pgs and pgs[0].edit():
                    return brev
                # Here, we failed to guess. Boohoo.
                raise ValueError(
                    "get_validation_event(): Could not find any event for "
                    "release {0} and date {1}.".format(release, date))

        elif self._check_compose(compose) == 'compose':
            compose = str(compose).upper()
            if not milestone:
                raise ValueError(
                    "get_validation_event(): For a TC/RC compose, a milestone "
                    "- Alpha, Beta, or Final - must be specified.")
            return ev.ComposeEvent(self, release, milestone, compose)
        else:
            # We should never get here, but just in case.
            raise ValueError(
                "get_validation_event(): Something very strange happened.")

    def get_validation_page(self, testtype, release='', milestone='',
                            compose=''):
        """Get an appropriate ValidationPage object for the values
        given. As with get_validation_event(), this method is for
        sloppy instantiation of pages that follow the rules. This
        method has no required arguments except the testtype and tries
        to figure out what you want from what you give it. It will
        raise errors if what you give it is impossible to interpret or
        if it tries and comes up with an inconsistent-seeming result.

        If you pass a numeric release, a milestone, and a valid
        compose (TC/RC or date), it will give you the appropriate
        event, whether it exists or not. All it really does in this
        case is pick NightlyEvent or ComposeEvent for you. If you
        don't fulfill any of those conditions, it'll need to do
        some guessing/assumptions, and in some of those cases it
        will only return an Event *that actually exists*, and may
        raise exceptions if you passed a particularly pathological
        set of values.

        If you don't pass a compose argument it will get the page for
        the current event; if you passed either of the other
        arguments and they don't match the current event, it will
        raise an error. It follows that calling this with no arguments
        just gives you the page of the specified test type for the
        current event.

        Various other guessing heuristics are applied. In all cases,
        if you don't pass a release, the release of the current event
        will be used instead. If you pass 'Rawhide' or 'Branched' as
        the release, it will be turned into the milestone and the
        release of the current event will be used as the release.

        If you pass a date as compose with no milestone, it will see
        if there's a Rawhide nightly and return it if so, otherwise it
        will see if there's a Branched nightly and return that if so,
        otherwise raise an error. It follows that you can't get the
        page for an event that *doesn't exist yet* this way: you must
        instantiate it directly or call this method with a milestone.

        It will not attempt to guess a milestone for TC/RC composes;
        it will raise an exception in this case.

        The guessing bits require wiki roundtrips, so they will be
        slower than instantiating a class directly or using this
        method with sufficient information to avoid guessing.
        """
        try:
            (release, milestone) = self._check_release_milestone(
                release, milestone)
        except ValueError as err:
            raise ValueError("get_validation_event(): {0}".format(err[0]))
        if not compose:
            # Can't really make an educated guess without a compose,
            # so just get the current event and return it if it
            # matches any other values passed.
            curr = self.current_compose
            page = self.get_validation_page(
                testtype, release=curr['release'], milestone=curr['milestone'],
                compose=max(curr['compose'], curr['date']))
            if (release and page.release != release):
                raise ValueError(
                    "get_validation_page(): Guessed page release {0} does "
                    "not match requested release {1}".format(
                        page.release, release))
            if (milestone and page.milestone != milestone):
                raise ValueError(
                    "get_validation_page(): Guessed page milestone {0} "
                    "does not match specified milestone {1}".format(
                        page.milestone, milestone))
            return page

        if self._check_compose(compose) == 'date':
            if milestone:
                return pg.NightlyPage(
                    self, release, testtype, milestone, compose)
            else:
                rawpg = pg.NightlyPage(
                    self, release, testtype, 'Rawhide', compose)
                if rawpg.exists:
                    return rawpg
                brpg = pg.NightlyPage(
                    self, release, testtype, 'Branched', compose)
                if brpg.exists:
                    return brpg
                # Here, we failed to guess. Boohoo.
                raise ValueError(
                    "get_validation_page(): Could not find any event for "
                    "release {0} and date {1}.".format(release, date))

        elif self._check_compose(compose) == 'compose':
            if not milestone:
                raise ValueError(
                    "get_validation_page(): For a TC/RC compose, a milestone "
                    "- Alpha, Beta, or Final - must be specified.")
            return pg.ComposePage(
                self, release, testtype, milestone, compose)
        else:
            # We should never get here, but just in case.
            raise ValueError(
                "get_validation_page(): Something very strange happened.")
