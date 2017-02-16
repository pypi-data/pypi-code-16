#!/bin/python2

# Copyright (C) 2015 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
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
# This file defines the various release classes used as the main entry
# points.

import koji
import os
import subprocess32

from operator import attrgetter

import fedfind.const
import fedfind.helpers
import fedfind.image
import fedfind.kojiclient

from fedfind.cached_property import cached_property

def get_release(release='', date=None, milestone='', compose=''):
    """Function to return an appropriate Release subclass for the given
    version information. Figures out if you want a nightly, compose,
    milestone, or stable release and gives it to you. Catches some
    nonsense choices. Tries to figure out the appropriate subclass
    (current, archive, core...) for stable releases. Won't do any
    clever guessing of 'current release' or date or anything like that,
    put that in callers if you want it.
    """
    # Handle date (nightly) cases first.
    if date and (str(release).lower() == 'rawhide' or not release):
        return RawhideNightly(date)
    if date and release:
        return BranchedNightly(date, release)

    # Now we know we have no date; we can error out if 'release' is wrong.
    if not release:
        raise TypeError("get_release() needs at least release or date.")
    if release == 'rawhide':
        raise TypeError("get_release(): release 'rawhide' needs a date.")

    # Now we've got a release that's not 'rawhide' but no date. First,
    # handle stable releases. milestone 'Final' and no compose == final
    # release.
    if not compose and (not milestone or milestone == 'Final'):
        if int(release) < 7:
            return CoreRelease(release)
        if int(release) < 20:
            return ArchiveRelease(release)
        # All the ways we can try to handle the stable vs. archived
        # cutoff are basically hideous. This is the one I'm picking.
        rel = ArchiveRelease(release)
        if not rel.exists:
            rel = CurrentRelease(release)
        return rel

    # By ze Process of Elimination, we've now got a release and at
    # least one of milestone and compose.
    if not milestone:
        raise TypeError("get_release(): compose without milestone is "
                          "nonsense. Stoppit.")
    if not compose:
        return Milestone(release, milestone)
    return Compose(release, milestone, compose)

class Query(object):
    """Small class for image queries. attr is the name of the object
    attribute against which this query should be run. Terms is an
    iterable of search terms. exact and neg are query parameters.
    If exact is True the match will succeed only on an exact match of
    any query term vs. the object attribute, otherwise the match will
    succeed if any query term is a substring of the object attribute.
    If neg is True, the result is reversed (turns IS into IS NOT and IN
    into NOT IN). Two false-y values are considered a match - if the
    query term is False or None or '' and the object attribute is False
    or None or '', the match succeeds. The object not having the
    attribute at all is treated identically to have it set to a false-y
    value."""
    def __init__(self, attr, terms, exact=True, neg=False):
        self.attr = attr
        self.getter = attrgetter(attr)
        self.terms = terms
        self.exact = exact
        self.neg = neg

    def _ci_match(self, a, b, exact, neg):
        """Case-insensitive match, handles either term being false-y."""
        if not a and not b:
            ret = True
        elif not a or not b:
            ret = False
        elif exact:
            ret = a.lower() == b.lower()
        else:
            ret = a.lower() in b.lower()
        if neg:
            return (not ret)
        return ret

    def match(self, obj):
        try:
            objval = self.getter(obj)
        except:
            objval = None
        return any(self._ci_match(t, objval, self.exact, self.neg)
                    for t in self.terms)

class Release(object):
    """Top level class for releases, providing shared attributes and
    methods. Should never be instantiated directly.
    """
    def __init__(self, date='', release='', milestone='', compose=''):
        self.release = release
        self.date = date
        self.milestone = milestone
        self.compose = compose

    def find_images(self, queries=list(), orq=False):
        """This is a simple 'fallback' query method which simply finds
        all images for the release and runs the query function. The
        idea is that subclasses should have more sophisticated
        find_images() methods which try to reduce the set of images
        queried when possible to improve performance. find_images()
        should always ultimately call _query_images() on the set of
        images it decides on, with the opts dict it was passed, to
        handle the query stuff.
        """
        if not queries:
            return self.all_images
        return self._query_images(queries, orq=orq)

    def _query_images(self, queries, imgs=None, orq=False):
        """This is a very generic method for searching a given set of
        images. opts is a dict whose keys are image attributes. If
        the image's attribute matches one of the values in the dict
        entry for that attribute, the check for that property passes.
        The default match is an exact match.

        There are some special 'values' that modify the query behavior.
        If one of the values is 'IN', images will match if any of the
        values is 'in' the relevant attribute (i.e. a substring match
        not an exact match). If one of the values is 'NOT', images
        will match as long as the relevant attribute is not an exact
        match for any of the query values. If one of the values is
        'NOTIN', images will match as long as none of the query values
        is 'in' the relevant attribute. The special values are never
        themselves matched, they only serve to modify the behavior.
        One handy case of this is to do a substring match on the whole
        image URL - dict(url=('blah', 'IN')) will find images with
        'blah' anywhere in their URL.

        Multi-attribute searches are AND by default - only images which
        have a match for every attribute in the opts dict will be
        returned. There is one special key which modifies this. If the
        dict contains the key 'OR', the search will be OR instead of
        AND; images which match on at least one of the query keys will
        be returned. The value of the 'OR' key is not used.

        Note you can use an empty string, '', as a query value - say
        you want to find all images which aren't for a Flavor, you
        could use dict(flavor=('',)) as the opts dict.
        """
        if orq:
            orset = set()
        if not imgs:
            imgs = self.all_images
        for query in queries:
            match = [i for i in imgs if query.match(i)]
            if orq:
                orset.update(match)
            else:
                imgs = match
        if orq:
            imgs = list(orset)
        return imgs

    def image_from_url_or_path(self, url='', path=''):
        """This gets an image instance for a given URL or mirror
        path, setting any properties that we know from the release's
        properties.
        """
        if not url and not path:
            raise TypeError("image_from_url_or_path() needs url or path.")
        return fedfind.image.Image(url=url, path=path, release=self.release,
                                    date=self.date, milestone=self.milestone,
                                    compose=self.compose)

    def get_mirror_images(self):
        """Find images in the main mirror tree by parsing rsync output.
        This is about the simplest / most reliable method I could
        figure out for scraping the mirror tree. _rsyncpath is the path
        prefix to restrict the search to.
        """
        # This excludes files but includes directories (we have to include
        # directories to be able to include their contents)
        args = ['/usr/bin/rsync', '{}/{}/'.format(fedfind.const.RSYNC,
                                                self._rsyncpath),
                '--recursive', '--exclude="*"', '--include="*/"']
        # This includes files that end with one of our image extensions
        args.extend(['--include="*{}"'.format(ext)
                    for ext in fedfind.const.IMAGE_EXTS])
        null = open(os.devnull)
        try:
            out = subprocess32.check_output(args, stderr=null)
        except:
            return []
        # This finds the output lines that are image files (ones ending with
        # our image extensions) and produces a URL by combining the base alt
        # URL with the file path, which is the fifth field of the rsync output
        paths = ['{}/{}'.format(self._rsyncpath, o.split()[4])
                for o in out.splitlines()
                for e in fedfind.const.IMAGE_EXTS if o.endswith(e)]
        return [self.image_from_url_or_path(path=path) for path in paths]

## NIGHTLY-TYPE RELEASE CLASSES ##

class Nightly(Release):
    """Parent class for nightly releases: Rawhide and Branched
    nightlies are very similar and share lots of logic, only a few
    details differ in the child classes. Should not be instantiated
    directly.
    """
    def __init__(self, date, release):
        super(Nightly, self).__init__(date=date, release=release)

    @cached_property
    def all_boot_images(self):
        imgs = list()
        for arch in fedfind.const.NIGHTLY_BOOT_ARCHES:
            img = self.image_from_url_or_path(url=self._get_boot_url(arch))
            if img.exists:
                imgs.append(img)
        return imgs

    @cached_property
    def all_koji_images(self):
        return self.get_koji_images()

    @cached_property
    def all_images(self):
        return self.all_boot_images + self.all_koji_images

    def _get_boot_url(self, arch):
        tmpl = '{}/{}/os/images/boot.iso'
        return tmpl.format(self.mashbase, arch)

    def check_koji_urls(self, opts=dict()):
        client = fedfind.kojiclient.get_client()
        urls = list()
        opts['states'] = [koji.TASK_STATES['CLOSED']]
        if 'method' not in opts:
            opts['method'] = 'createLiveCD'
        tasks = client.find_nightly_tasks(date=self.date, release=self.release,
                                   opts=opts)
        for t in tasks:
            try:
                urls.append(client.find_task_url(t))
            except:
                pass
        return urls

    def get_koji_images(self,
            methods=('createLiveCD', 'createAppliance', 'createImage'),
            arches=None):
        imgs = list()
        for method in methods:
            opts = dict()
            opts['method'] = method
            if arches:
                opts['arch'] = list(arches)
            imgs.extend([self.image_from_url_or_path(url=url)
                         for url in self.check_koji_urls(opts)])
        return imgs

    def find_images(self, queries=list(), orq=False):
        if not queries:
            return self.all_images
        arches = None
        bootimgs = kojiimgs = list()
        needboot = needlive = needdisk = True
        for query in queries:
            # We can only narrow down the external queries if the fedfind query
            # is positive and exact.
            if query.attr == 'imagetype' and not query.neg and query.exact:
                if 'boot' not in query.terms:
                    needboot = False
                if 'live' not in query.terms:
                    needlive = False
                if 'disk' not in query.terms:
                    needdisk = False
                arches = query.terms

        if needboot:
            bootimgs = self.all_boot_images

        methods = list()
        if needlive and needdisk and not arches:
            kojiimgs = self.all_koji_images

        if needlive:
            methods.append('createLiveCD')
        if needdisk:
            methods.extend(['createAppliance', 'createImage'])
        if methods and not kojiimgs:
            kojiimgs = self.get_koji_images(methods=methods, arches=arches)

        imgs = bootimgs+kojiimgs
        return self._query_images(queries, imgs, orq=orq)


class RawhideNightly(Nightly):
    """A Rawhide nightly 'release', consisting of the nightly composes
    for the Rawhide branch for the specified date.
    """
    def __init__(self, date):
        release = 'rawhide'
        self.mashbase = '{}/rawhide-{}/rawhide'.format(
                fedfind.const.MASH_BASE, date.strftime('%Y%m%d'))
        super(RawhideNightly, self).__init__(date, release)


class BranchedNightly(Nightly):
    """A Branched nightly 'release', consisting of the nightly composes
    for the Branched branch for the specified date. Given how the
    mash directory is laid out, you have to specify a release; it's
    not feasible to just find 'the' Branched 'release' for a given
    date. Callers that want to be helpful could make a sensible guess
    like 'current release plus one', though - that's usually the only
    one you'll be interested in and able to find any images for.
    """
    def __init__(self, date, release):
        release = str(release)
        self.mashbase = '{}/branched-{}/{}'.format(
                fedfind.const.MASH_BASE, date.strftime('%Y%m%d'), release)
        super(BranchedNightly, self).__init__(date, release)

## END NIGHTLY-TYPE RELEASE CLASSES ##

class MirrorRelease(Release):
    """A parent class for releases for which all files are on the
    mirrors (no koji or mash stuff)."""
    def __init__(self, release, milestone='', compose=''):
        super(MirrorRelease, self).__init__(
                release=release, milestone=milestone, compose=compose)

    @cached_property
    def all_images(self):
        return self.get_mirror_images()

    @cached_property
    def exists(self):
        url = '{}/{}'.format(fedfind.const.RSYNC, self._rsyncpath)
        return fedfind.helpers.url_exists(url)

class Compose(MirrorRelease):
    """A TC/RC compose, stored in the staging tree."""
    def __init__(self, release, milestone, compose):
        super(Compose, self).__init__(release=release, milestone=milestone,
                                      compose=compose)
        if self.milestone == 'Final':
            self._rsyncpath = 'alt/stage/{}_{}'.format(
                    self.release, self.compose)
        else:
            self._rsyncpath = 'alt/stage/{}_{}_{}'.format(
                    self.release, self.milestone, self.compose)

class Milestone(MirrorRelease):
    """A milestone release - Alpha or Beta."""
    def __init__(self, release, milestone):
        super(Milestone, self).__init__(release=release, milestone=milestone)
        self._rsyncpath = 'fedora/linux/releases/test/{}-{}'.format(
            release, milestone)

## STABLE RELEASE CLASSES ##

class CurrentRelease(MirrorRelease):
    """A release that public mirrors are expected to carry (not an
    archived one).
    """
    def __init__(self, release):
        super(CurrentRelease, self).__init__(release=release)
        self._rsyncpath = 'fedora/linux/releases/{}'.format(release)

class ArchiveRelease(MirrorRelease):
    """An archived Fedora (post-Fedora Core) release."""
    def __init__(self, release):
        super(ArchiveRelease, self).__init__(release=release)
        self._rsyncpath = 'archive/fedora/linux/releases/{}'.format(release)


class CoreRelease(MirrorRelease):
    """A Fedora Core release."""
    def __init__(self, release):
        super(CoreRelease, self).__init__(release=release)
        self._rsyncpath = 'archive/fedora/linux/core/{}'.format(release)

## END STABLE RELEASE CLASSES ##
