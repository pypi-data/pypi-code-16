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
#
# This file kind of shadows mwclient's listing.py, creating modified
# versions of several of its classes. The point is to provide generators
# similar to mwclient's own, but which return wikitcms page/category
# instances when appropriate, falling through to mwclient instances
# otherwise.

from . import page as pg

from mwclient import listing as mwl
import re

# exceptions: the wikitcms getter raises these when it fails rather than
# just returning None, so the generators can use try/except blocks to
# handle both this case and the case (which shouldn't ever happen, but
# just in case) where they're being used on something other than a list
# of pages.

class NoPageWarning(Exception):
    """Exception raised when the tcmswiki getter can't find a matching
    page. Not really an error, should always be handled.
    """
    def __init__(self, page):
        self.page = page

    def __str__(self):
        return ("Could not produce a wikitcms page for: {0}".format(self.page))


class PageCheckWarning(Exception):
    """Exception raised when the wikitcms getter finds a matching page,
    but the page name the class generators from the page's various
    attributes doesn't match the page name the getter was given. Should
    usually be handled (and an mwclient Page instance returned instead).
    """
    def __init__(self, frompage, topage):
        self.frompage = frompage
        self.topage = topage

    def __str__(self):
        return ("Expected page name {0} does not match source page name {1}"
                 .format(self.frompage, self.topage))


class TcmsGeneratorList(mwl.GeneratorList):
    """A GeneratorList which returns wikitcms page (and category etc.)
    instances when appropriate. _get_tcms is implemented as a separate
    function so TcmsPageList can use the discovery logic.
    """
    def __init__(self, site, list_name, prefix, *args, **kwargs):
        super(TcmsGeneratorList, self).__init__(site, list_name, prefix,
              *args, **kwargs)

    def next(self):
        # We can't get the next entry from mwl.List ourselves, try and
        # handle it, then pass it up to our parent if we can't, because
        # parent's next() gets the next entry from mwl.List itself, so
        # in that scenario, one list item gets skipped. Either we
        # entirely clone next() with our own additions, or we let it
        # fire and then override the result if we can. Using nxt._info
        # is bad, but super.next() doesn't return that, and the page
        # instance doesn't expose it any other way. We could just use
        # the name, but if you don't pass info when instantiating a
        # Page, it has to hit the API during init to reconstruct info,
        # and that causes a massive performance hit.
        nxt = super(TcmsGeneratorList, self).next()
        try:
            return self._get_tcms(nxt.name, nxt._info)
        except:
            return nxt

    def _check_page(self, name, page):
        # convenience function for _get_tcms sanity check
        if page.checkname == name:
            return page
        raise PageCheckWarning(page.checkname, name)

    def _get_tcms(self, name, info=()):
        # this is the meat: it runs a bunch of string checks on page
        # names, basically, and returns the appropriate wikitcms
        # object if any matches.
        if type(name) is int:
            # we'll have to do a wiki roundtrip, as we need the text
            # name.
            page = pg.Page(name)
            name = page.name
        name = name.replace('_', ' ')
        # quick non-RE check to see if we'll ever match
        if (name.startswith(u'Test Results:') or
            name.startswith(u'Test Day:') or
                (name.startswith(u'Category:') and
                 name.endswith(u'Test Results'))):
            nightly_patt = re.compile(u'Test Results:Fedora (\d{1,3}) '
                                      '(Rawhide|Nightly) '
                                      '(\d{8,8}|\d{4,4} \d{2,2}) (.+)$')
            accept_patt = re.compile(u'Test Results:Fedora (\d{1,3}) '
                                     '([^ ]+?) (Rawhide |)Acceptance Test '
                                     '(\d{1,2})$')
            ms_patt = re.compile(u'Test Results:Fedora (\d{1,3}) '
                                 '([^ ]+?) ([^ ]+?) (.+)$')
            cat_patt = re.compile(u'Category:Fedora (\d{1,3}) '
                                  '(.*?) *?Test Results$')
            testday_patt = re.compile(u'Test Day:(\d{4}-\d{2}-\d{2}) ([^/]+)$')
            # FIXME: There's a few like this, handle 'em sometime
            #testday2_patt = re.compile(u'Test Day:(.+) (\d{4}-\d{2}-\d{2})$')

            # Modern standard nightly compose event pages, and F21-era
            # monthly Rawhide/Branched test pages
            match = nightly_patt.match(name)
            if match:
                if match.group(4) == 'Summary':
                    # we don't really ever need to do anything to existing
                    # summary pages, and instantiating one from here is kinda
                    # gross, so just fall through
                    raise NoPageWarning(name)
                page = pg.NightlyPage(self.site, match.group(1),
                        match.group(4), tree=match.group(2),
                        date=match.group(3), info=info)
                return self._check_page(name, page)

            match = accept_patt.match(name)
            if match:
                # we don't handle these, yet.
                raise NoPageWarning(name)

            # milestone compose event pages
            match = ms_patt.match(name)
            if match:
                if match.group(4) == 'Summary':
                    raise NoPageWarning(name)
                page = pg.ComposePage(self.site, match.group(1),
                        match.group(4), milestone=match.group(2),
                        compose=match.group(3), info=info)
                return self._check_page(name, page)

            # test result categories
            match = cat_patt.match(name)
            if match:
                if not match.group(2):
                    page = TcmsCategory(self.site, match.group(1), info=info)
                    return self._check_page(name, page)
                elif match.group(2) == 'Nightly':
                    page = TcmsCategory(self.site, match.group(1),
                                        nightly=True, info=info)
                    return self._check_page(name, page)
                else:
                    page = TcmsCategory(self.site, match.group(1),
                                        match.group(2), info=info)
                    return self._check_page(name, page)

            # test days
            match = testday_patt.match(name)
            if match:
                page = pg.TestDayPage(self.site, match.group(1), match.group(2),
                                      info=info)
                return self._check_page(name, page)
        raise NoPageWarning(name)


class TcmsPageList(mwl.PageList, TcmsGeneratorList):
    """A version of PageList which returns wikitcms page (and category
    etc.) objects when appropriate.
    """
    # This is just PageList's __init__, fixed:
    # https://github.com/mwclient/mwclient/pull/75
    def __init__(self, site, prefix=None, start=None, namespace=0,
                 redirects='all'):
        self.namespace = namespace
        kwargs = {}
        if prefix:
            kwargs['gapprefix'] = prefix
        if start:
            kwargs['gapfrom'] = start

        TcmsGeneratorList.__init__(self, site, 'allpages', 'ap',
                               gapnamespace=mwl.text_type(namespace),
                               gapfilterredir=redirects, **kwargs)

    def get(self, name, info=()):
        modname = name
        if self.namespace:
            modname = '{0}:{1}'.format(self.site.namespaces[self.namespace],
                                       name)
        try:
            return self._get_tcms(modname, info)
        except:
            return super(TcmsPageList, self).get(name, info)


class TcmsCategory(pg.Page, TcmsGeneratorList):
    """A modified category class - just as mwclient's Category class
    inherits from both its Page class and its GeneratorList class,
    acting as both a page and a generator returning the members of
    the category, so this inherits from wikitcms' Page and
    TcmsGeneratorList. You can produce the page contents with pg.Page
    write() method, and you can use it as a generator which returns
    the category's members, as wikitcms class instances if appropriate
    or mwclient class instances otherwise. It works recursively - if
    a member of a TcmsCategory is itself a test category, you'll get
    another TcmsCategory instance.

    If nightly is True, this will be a category for test results from
    Rawhide or Branched nightly builds for the given release.
    Otherwhise, if milestone is passed, this will be a category for
    the given milestone, and if it isn't, it will be the top-level
    category for the given release.
    """

    def __init__(self, site, release, milestone=None, nightly=False, info=None):
        if nightly is True:
            wikiname = ("Category:Fedora {0} Nightly Test "
                             "Results").format(release)
            self.seedtext = ("{{{{Validation results milestone category|release="
                         "{0}|nightly=true}}}}").format(release)
            self.summary = ("Relval bot-created validation result category page"
                            " for Fedora {0} nightly results").format(release)
        elif milestone:
            wikiname = "Category:Fedora {0} {1} Test Results".format(
                    release, milestone)
            self.seedtext = ("{{{{Validation results milestone category|release="
                         "{0}|milestone={1}}}}}").format(release, milestone)
            self.summary = ("Relval bot-created validation result category page"
                            " for Fedora {0} {1}").format(release, milestone)
        else:
            wikiname = "Category:Fedora {0} Test Results".format(release)
            self.seedtext = ("{{{{Validation results milestone category|release="
                         "{0}}}}}").format(release)
            self.summary = ("Relval bot-created validation result category page"
                            " for Fedora {0}").format(release)

        super(TcmsCategory, self).__init__(site, wikiname, info=info)
        TcmsGeneratorList.__init__(self, site, 'categorymembers', 'cm',
                                   gcmtitle=self.name)
