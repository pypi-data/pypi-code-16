#!/usr/bin/python2

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

"""Defines the various release classes used as the main entry
points.
"""

import abc
import datetime
import os
# Upstream docs recommend using subprocess32 if possible, but make
# this optional as it's not available in EPEL.
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

from operator import attrgetter

import fedfind.const
import fedfind.exceptions
import fedfind.helpers
import fedfind.image
import fedfind.kojiclient

from fedfind.cached_property import cached_property

def get_release(release='', milestone='', compose=''):
    """Function to return an appropriate Release subclass for the
    version information. Figures out if you want a nightly, compose,
    milestone, or stable release and gives it to you. Catches some
    nonsense choices. Tries to figure out the appropriate subclass
    (current, archive, core...) for stable releases. Won't do any
    clever guessing of 'current release' or date or anything like
    that. Put that in callers if you want it. For nightlies, pass
    compose as 'YYYYMMDD' or a datetime.date object. If 'release' is
    digits or an int and milestone is not something that looks like
    'rawhide', you'll get a BranchedNightly for that release,
    otherwise you'll get a RawhideNightly. This should be mostly
    compatible with python-wikitcms release/milestone/compose concept:
    you should always be able to get the right result by passing
    a python-wikitcms release/milestone/compose to fedfind. It will
    usually work the other way, but it relies on python-wikitcms
    guessing a release number for Rawhide nightlies; in fedfind,
    no release number is associated with Rawhide nightlies. This is
    intentional, because Rawhide nightlies *per se* do not have a
    release number, Rawhide is a rolling distribution. We 'declare'
    a Fedora release number for Rawhide nightly *test events*: the
    release number is strictly speaking a property of the event, not
    the compose or the images.
    """
    if not release and not compose:
        if milestone:
            raise ValueError("get_release(): cannot guess safely from "
                             "a milestone but nothing else.")
        # Just try today's Rawhide nightly and hope for the best.
        return RawhideNightly(compose=datetime.date.today())

    # Otherwise...handle nightly cases first. Intent:
    #
    # * Rawhide YYYYMMDD = Rawhide
    # NN [anything-but-Rawhide] YYYYMMDD = Branched
    # [anything-but-NN] [anything-but-Branched] YYYYMMDD = Rawhide
    # [anything-but-NN] Branched YYYYMMDD = error (can't guess release)
    #
    # Note Branched [anything-but-Branched] YYYYMMDD will return
    # Rawhide. That's OK, because 'Branched' as release is just flat
    # wrong. Don't do that.
    date = fedfind.helpers.date_check(compose, fail_raise=False)
    if date:
        if str(release).isdigit() and not 'rawhide' in str(milestone).lower():
            return BranchedNightly(release=release, compose=date)
        elif 'branched' in str(milestone).lower():
            raise ValueError("get_release(): cannot guess a release number "
                             "for a Branched compose. Please specify it.")
        else:
            return RawhideNightly(compose=date)

    # We know compose is not a date; we now require a numeric release.
    if not release:
        raise ValueError("get_release(): must specify at least a numeric "
                         "release if compose is not a date.")
    elif not str(release).isdigit():
        raise ValueError("get_release(): non-numeric 'release' needs a date.")

    # Now we've got a release that's a number, and compose is not a
    # date. We *don't* know if we have milestone or compose at all.
    # First, handle stable releases: note that if milestone is 'Final'
    # and there is no compose we assume you want the final release.
    if not compose and (not milestone or str(milestone).lower() == 'final'):
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
    # least one of milestone and (non-date) compose.
    if not milestone:
        raise ValueError("get_release(): cannot guess safely from a non-date "
                         "milestone but nothing else.")
    if not compose:
        # We *expect* this to be something like '22 Alpha', but just
        # in case we get something like '22 Rawhide' or '22 Branched',
        # give 'em today's compose.
        if milestone.lower() == 'rawhide':
            return RawhideNightly(compose=datetime.date.today())
        if milestone.lower() == 'branched':
            return BranchedNightly(
            release=release, compose=datetime.date.today())
        # This is the *expected* case
        else:
            return Milestone(release, milestone)
    # Here we have a release, milestone, and non-date compose.
    return Compose(release, milestone, compose)

class Query(object):
    """Small class for image queries. attr is the name of the object
    attribute against which this query should be run. Terms is an
    iterable of search terms. exact and neg are query parameters.
    If exact is True the match will succeed only on an exact match of
    any query term vs. the object attribute, otherwise the match will
    succeed if any query term is a substring of the object attribute.
    If neg is True, the result is reversed (turns IS into IS NOT and
    IN into NOT IN). Two false-y values are considered a match - if
    the query term is False or None or '' and the object attribute is
    False or None or '', the match succeeds. The object not having the
    attribute at all is treated identically to have it set to a falsey
    value."""
    def __init__(self, attr, terms, exact=True, neg=False):
        self.attr = attr
        self.getter = attrgetter(attr)
        self.terms = terms
        self.exact = exact
        self.neg = neg

    def match(self, obj):
        """Perform the match (for details see class docstring)."""
        try:
            objval = self.getter(obj)
        except AttributeError:
            objval = None
        return any(fedfind.helpers.ci_match(t, objval, self.exact, self.neg)
                   for t in self.terms)

class Release(object):
    """Abstract class for releases, providing shared attributes and
    methods.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, release='', milestone='', compose=''):
        self.release = str(release).capitalize()
        self.milestone = str(milestone).capitalize()
        try:
            (self.compose, self._dateobj) = fedfind.helpers.date_check(
                compose, fail_raise=True, out='both')
        except ValueError:
            (self.compose, self._dateobj) = (str(compose).upper(), None)
        # this will usually match the wikitcms 'version' concept, but
        # not always, significantly not for Rawhide nightlies. There's
        # a whole existential can o' worms there.
        self.version = self.release
        if self.milestone:
            self.version += ' {0}'.format(self.milestone)
        if self.compose:
            self.version += ' {0}'.format(self.compose)

    @abc.abstractproperty
    def all_images(self):
        """All images for this release."""
        pass

    @abc.abstractproperty
    def exists(self):
        """Whether the release is considered to 'exist'."""
        pass

    @abc.abstractproperty
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
        subdirectories are named for primary arches and contain
        .treeinfo files, and where the 'generic' network install
        image for the release was built from).
        """
        pass

    def find_images(self, queries=None, orq=False):
        """This is a simple 'fallback' query method which simply finds
        all images for the release and runs the query function. The
        idea is that subclasses can have more sophisticated
        find_images() methods which try to reduce the set of images
        queried when possible to improve performance. find_images()
        should always ultimately call _query_images() on the set of
        images it decides on, with the iterable of queries it was
        passed, to handle the query stuff. See the _query_images()
        docstring for details on queries and orq.
        """
        if not queries:
            return self.all_images
        return self._query_images(queries, orq=orq)

    def _query_images(self, queries, imgs='all', orq=False):
        """This is a very generic method for searching a given set of
        images. queries is an iterable of Query objects (or I guess
        an iterable whose members can be any objects with a 'match'
        method that you want to use to filter the image list). Refer
        to the Query class docstrings for more details on how to
        create appropriate queries.

        imgs is an iterable of fedfind.Image objects to query. If left
        at its default value, all images (the all_images property)
        will be queried.

        Multi-attribute searches are AND by default - only images for
        which every query.match() call passes will be returned. You
        can pass orq=True to change this behavior to OR, in which case
        images for which *any* query.match() call passes will be
        returned.
        """
        if orq:
            orset = set()
        if imgs == 'all':
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
        return fedfind.image.Image(
            url=url, path=path, release=self.release,
            milestone=self.milestone, compose=self.compose)

## NIGHTLY-TYPE RELEASE CLASSES ##

class Nightly(Release):
    """Parent class for nightly releases: Rawhide and Branched
    nightlies are very similar and share lots of logic, only a few
    details differ in the child classes. Should not be instantiated
    directly.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, compose, release='', milestone=''):
        super(Nightly, self).__init__(
            release=release, milestone=milestone, compose=compose)

    @cached_property
    def all_boot_images(self):
        """All boot.iso-type images. We can get these without hitting
        Koji.
        """
        imgs = list()
        arches = (a.name for a in fedfind.const.ARCHES if a.current)
        for arch in arches:
            img = self.image_from_url_or_path(url=self._get_boot_url(arch))
            if img.exists:
                imgs.append(img)
        return imgs

    @cached_property
    def all_koji_images(self):
        """All images we have to get from Koji."""
        return self.get_koji_images()

    @cached_property
    def all_images(self):
        """All images for this release."""
        return self.all_boot_images + self.all_koji_images

    @cached_property
    def exists(self):
        return fedfind.helpers.url_exists(self.https_url_generic)

    def _get_boot_url(self, arch):
        """Get the expected URL for the boot.iso of a given arch."""
        tmpl = '{0}/{1}/os/images/boot.iso'
        return tmpl.format(self.https_url_generic, arch)

    def _check_koji_urls(self, opts=None):
        """Query Koji for nightly tasks, and return a list of image
        URLs. By default finds all live images. opts is an opts dict
        for the koji listTasks() method; the purpose of passing one
        from here is to specify the method we want to find images
        for. Used by get_koji_images()."""
        client = fedfind.kojiclient.ClientSession(
            'http://koji.fedoraproject.org/kojihub')
        if not opts:
            opts = dict()
        urls = list()
        # KOJI: as we're trying to avoid using the koji module, this
        # value is hard-coded. It means 'CLOSED'. Ideally we would use
        # koji.TASK_STATES['CLOSED'] here.
        opts['states'] = [2]
        if 'method' not in opts:
            opts['method'] = 'createLiveCD'
        tasks = client.find_nightly_tasks(
            date=self._dateobj, release=self.release, opts=opts)
        for task in tasks:
            try:
                urls.append(client.find_task_url(task))
            except (fedfind.exceptions.NoImageError,
                    fedfind.exceptions.NoFilesError):
                pass
        return urls

    def get_koji_images(
            self, methods=('createLiveCD', 'createAppliance', 'createImage'),
            arches=None):
        """Find all or some of our Koji nightly tasks, and return a
        list of fedfind.Image instances, one per task that produced
        images. Methods is an iterable of Koji task methods (each
        method requires another query, so we want to be able to limit
        this to as few methods as possible when we can).
        """
        imgs = list()
        for method in methods:
            opts = dict()
            opts['method'] = method
            if arches:
                opts['arch'] = list(arches)
            imgs.extend([self.image_from_url_or_path(url=url)
                         for url in self._check_koji_urls(opts)])
        return imgs

    def find_images(self, queries=None, orq=False):
        """This implementation tries to speed up certain queries by
        avoiding some remote queries where possible. If we are only
        asked for boot images, it doesn't hit Koji. If we *aren't*
        asked for boot images, it doesn't hit the mirrors. If we are
        only asked for certain types of image, it restricts the list
        of methods we query Koji for (each method requires an extra
        query).
        """
        if not queries:
            return self.all_images
        arches = None
        bootimgs = kojiimgs = list()
        needboot = needlive = needdisk = True
        for query in queries:
            # We can only narrow down the external queries if the
            # fedfind query is positive and exact.
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
    for the Rawhide branch for the specified compose (a date) - the
    slightly obtuse name is following the broader conventions for all
    fedfind/wikitcms version naming.
    """
    def __init__(self, compose):
        super(RawhideNightly, self).__init__(
            release='Rawhide', compose=compose)

    @property
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
        subdirectories are named for primary arches and contain
        .treeinfo files, and where the 'generic' network install
        image for the release was built from).
        """
        return '{0}/rawhide-{1}/rawhide'.format(
            fedfind.const.MASH_BASE, self.compose)


class BranchedNightly(Nightly):
    """A Branched nightly 'release', consisting of the nightly composes
    for the Branched branch for the specified date. Given how the
    mash directory is laid out, you have to specify a release; it's
    not feasible to just find 'the' Branched 'release' for a given
    date. Callers that want to be helpful could make a sensible guess
    like 'current release plus one', though - that's usually the only
    one you'll be interested in and able to find any images for.
    """
    def __init__(self, compose, release):
        super(BranchedNightly, self).__init__(
            release=release, milestone='Branched', compose=compose)

    @property
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
        subdirectories are named for primary arches and contain
        .treeinfo files, and where the 'generic' network install
        image for the release was built from).
        """
        return '{0}/branched-{1}/{2}'.format(
            fedfind.const.MASH_BASE, self.compose, self.release)

## END NIGHTLY-TYPE RELEASE CLASSES ##

class MirrorRelease(Release):
    """A parent class for releases for which all files are on the
    mirrors (no koji or mash stuff)."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, release, milestone='', compose=''):
        super(MirrorRelease, self).__init__(
            release=release, milestone=milestone, compose=compose)

    @abc.abstractproperty
    def _rsyncpath(self):
        """Top level path for this release, relative to the fedora-
        buffet bundle in rsync (/pub on the master mirror).
        """
        pass

    @cached_property
    def all_images(self):
        """All images for this release."""
        return self.get_mirror_images()

    @cached_property
    def exists(self):
        """Release 'exists' if its top-level mirror path is there."""
        url = '{0}/{1}'.format(fedfind.const.RSYNC, self._rsyncpath)
        return fedfind.helpers.url_exists(url)

    @property
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
        subdirectories are named for primary arches and contain
        .treeinfo files, and where the 'generic' network install
        image for the release was built from).
        """
        if int(self.release) < 7:
            tmpl = '{0}/{1}'
        elif int(self.release) < 21:
            tmpl = '{0}/{1}/Fedora'
        elif int(self.release) >= 21:
            tmpl = '{0}/{1}/Server'
        return tmpl.format(fedfind.const.HTTPS, self._rsyncpath)

    def get_mirror_images(self):
        """Find images in the main mirror tree by parsing rsync output.
        This is about the simplest / most reliable method I could
        figure out for scraping the mirror tree. _rsyncpath is the path
        prefix to restrict the search to.
        """
        # This excludes files but includes directories (we have to
        # include directories to be able to include their contents)
        args = ['/usr/bin/rsync', '{0}/{1}/'.format(fedfind.const.RSYNC,
                                                    self._rsyncpath),
                '--recursive', '--exclude="*"', '--include="*/"']
        # This includes files that end with one of our image
        # extensions
        args.extend(['--include="*{0}"'.format(ext)
                     for ext in fedfind.const.IMAGE_EXTS])
        null = open(os.devnull)
        # Doesn't use check_output as it's not in Python 2.6
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=null)
        out = process.communicate()[0]
        retcode = process.poll()
        if retcode:
            return []
        # This finds the output lines that are image files (ones
        # ending with our image extensions) and produces a URL by
        # combining the base alt URL with the file path, which is the
        # fifth field of the rsync output
        paths = ['{0}/{1}'.format(self._rsyncpath, o.split()[4])
                 for o in out.splitlines()
                 for e in fedfind.const.IMAGE_EXTS if o.endswith(e)]
        return [self.image_from_url_or_path(path=path) for path in paths]


class Compose(MirrorRelease):
    """A TC/RC compose, stored in the staging tree."""
    def __init__(self, release, milestone, compose):
        super(Compose, self).__init__(
            release=release, milestone=milestone, compose=compose)

    @property
    def _rsyncpath(self):
        if self.milestone == 'Final':
            return 'alt/stage/{0}_{1}'.format(self.release, self.compose)
        else:
            return 'alt/stage/{0}_{1}_{2}'.format(
                self.release, self.milestone, self.compose)

class Milestone(MirrorRelease):
    """A milestone release - Alpha or Beta."""
    def __init__(self, release, milestone):
        super(Milestone, self).__init__(release=release, milestone=milestone)

    @property
    def _rsyncpath(self):
        return 'fedora/linux/releases/test/{0}-{1}'.format(
            self.release, self.milestone)

## STABLE RELEASE CLASSES ##

class CurrentRelease(MirrorRelease):
    """A release that public mirrors are expected to carry (not an
    archived one).
    """
    def __init__(self, release):
        super(CurrentRelease, self).__init__(release=release)

    @property
    def _rsyncpath(self):
        return 'fedora/linux/releases/{0}'.format(self.release)

class ArchiveRelease(MirrorRelease):
    """An archived Fedora (post-Fedora Core) release."""
    def __init__(self, release):
        super(ArchiveRelease, self).__init__(release=release)

    @property
    def _rsyncpath(self):
        return 'archive/fedora/linux/releases/{0}'.format(self.release)


class CoreRelease(MirrorRelease):
    """A Fedora Core release."""
    def __init__(self, release):
        super(CoreRelease, self).__init__(release=release)

    @property
    def _rsyncpath(self):
        return 'archive/fedora/linux/core/{0}'.format(self.release)

## END STABLE RELEASE CLASSES ##
