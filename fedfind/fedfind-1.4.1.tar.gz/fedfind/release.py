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
import json
import logging
import os
import six

from operator import attrgetter
from cached_property import cached_property
from decimal import (Decimal, InvalidOperation)

import fedfind.const
import fedfind.exceptions
import fedfind.helpers
import fedfind.image
import fedfind.kojiclient

logger = logging.getLogger(__name__)

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
        if milestone and milestone.lower() == "branched":
            # set date to today and keep going so we hit the Branched
            # guessing below and return today's Branched.
            compose = datetime.date.today()
        elif not milestone or milestone.lower() == 'rawhide':
            # Just try today's Rawhide nightly and hope for the best.
            return RawhideNightly(compose=datetime.date.today())
        else: # we've got a milestone that's not Rawhide or Branched.
            raise ValueError("get_release(): cannot guess safely from "
                             "a non-nightly milestone but nothing else.")

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
            rels = []
            # This is icky, but we have various needs for fedfind to
            # do branched release guessing. We're gonna scrape the
            # development/ directory and take the highest integer we
            # find, basically.
            args = ['{0}/{1}/'.format(fedfind.const.RSYNC,
                                      '/fedora/linux/development/'),
                    '--no-motd', '--include=[0-9][0-9]', '--exclude=**']
            (retcode, out) = fedfind.helpers.rsync_helper(args, True)
            if retcode:
                pass # we'll raise in the 'if rels' clause later
            else:
                rels = []
                for line in out.splitlines():
                    if line.split(' ')[-1].isdigit():
                        rels.append(int(line.split(' ')[-1]))

            if rels:
                return BranchedNightly(release=max(rels), compose=date)
            else:
                raise ValueError(
                    "get_release(): Guessing release number for Branched "
                    "compose failed. Please specify it.")
        else:
            return RawhideNightly(compose=date)

    # We know compose is not a date; we now require a numeric release.
    if not release:
        raise ValueError("get_release(): must specify at least a numeric "
                         "release if compose is not a date.")
    elif not str(release).isdigit():
        raise ValueError("get_release(): non-numeric 'release' needs a date.")
    if int(release) < 1:
        raise ValueError("get_release(): there are no release numbered lower "
                         "than 1.")

    # Now we've got a release that's a number, and compose is not a
    # date. We *don't* know if we have milestone or compose at all.
    # First, handle stable releases: note that if milestone is 'Final'
    # and there is no compose we assume you want the final release.
    if not compose and (not milestone or str(milestone).lower() == 'final'):
        if int(release) < 7:
            return CoreRelease(release)
        if int(release) < 21:
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
        # Handle a single search term passed as a string
        if isinstance(terms, six.string_types):
            terms = (terms,)
        self.terms = terms
        self.exact = exact
        self.neg = neg

    def __repr__(self):
        return "{0}({1}, {2}, exact={3}, neg={4})".format(
            self.__class__, self.attr, self.terms, self.exact,
            self.neg)

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

    def __repr__(self):
        return "{0}(release='{1}', milestone='{2}', compose='{3}')".format(
            self.__class__, self.release, self.milestone,
            self.compose)

    def __str__(self):
        return "{0} {1}".format(self.__class__.__name__, self.version)

    @abc.abstractproperty
    def previous_release(self):
        """The previous release of the same series. Like follows like,
        in this case: the 'previous' release for a stable release is
        the previous stable release, not the last RC. Cannot be relied
        upon for all cases, there are some where it's just too icky:
        will raise a ValueError in that case. May also return a
        release that never existed (in the case of the very first
        Branched nightly for a release, for instance), a release that
        existed but no longer does (an old milestone), or a release
        that does not yet exist but may later."""
        pass

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

    @abc.abstractproperty
    def expected_images(self):
        """These are the most important images that should be expected
        to exist for a release of the given type. Basically if any of
        these images does not exist, we ought to be worried. Pretty
        close to the concept of a 'release blocking' image, but I
        didn't want to commit to this being exactly that. Must be an
        iterable of (payload, imagetype, arch) tuples.
        """
        pass

    @abc.abstractproperty
    def koji_done(self):
        """Whether all Koji tasks for the compose are complete."""
        pass

    @abc.abstractproperty
    def pungi_done(self):
        """Whether all Pungi tasks for the compose are complete."""
        pass

    def difference(self, other):
        """Similarly to the behaviour of the set.difference() method,
        this tells you which images exist for this release but not
        for other. Returns a set of (payload, imagetype, arch) tuples
        identifying the unique images. 'other' must be another Release
        instance (you may often want to use self.previous_release).
        """
        ours = set(
            (img.payload, img.imagetype, img.arch) for img in self.all_images)
        theirs = set(
            (img.payload, img.imagetype, img.arch) for img in other.all_images)
        return ours.difference(theirs)

    def check_expected(self):
        """This checks whether all expected images are included in the
        release. If the release doesn't exist, it will raise an
        exception. If any expected images are missing, it will return
        a set of (payload, imagetype, arch) tuples identifying the
        missing images. If nothing is missing, it will return an empty
        set.
        """
        if not self.exists:
            raise ValueError('Release does not exist!')
        missing = set()
        for (payload, imagetype, arch) in self.expected_images:
            queries = (
                Query('payload', payload),
                Query('imagetype', imagetype),
                Query('arch', arch),
            )
            # This is a bit of a hack, but we happen to know that
            # we'll need to check basically all the images, and for
            # nightlies it's actually slower to use the 'optimised'
            # method in this case because it doesn't cache all its
            # results
            res = self._query_images(queries)
            if res:
                logger.debug('check_expected: found %s', res)
            else:
                missing.add((payload, imagetype, arch))
        return missing

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

    def image_from_url_or_path(self, url='', path='', prefurl=''):
        """This gets an image instance for a given URL or mirror
        path, setting any properties that we know from the release's
        properties.
        """
        return fedfind.image.Image(
            url=url, path=path, release=self.release,
            milestone=self.milestone, compose=self.compose, prefurl=prefurl)

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
        # Used to cache Koji search results
        self._kojicache = dict()

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

    @property
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

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. For a nightly release we expect for the Intel arches a
        generic boot.iso and Workstation and KDE live images, and for
        ARM we expect a minimal and a KDE disk image. For Cloud we
        expect, er, FIXME?
        """
        imgs = list()
        intels = (arch.name for arch in fedfind.const.ARCHES if
                  arch.group == 'intel')
        arms = (arch.name for arch in fedfind.const.ARCHES if
                arch.group == 'arm')
        for arch in intels:
            imgs.append(('generic', 'boot', arch))
            imgs.append(('workstation', 'live', arch))
            imgs.append(('kde', 'live', arch))
        for arch in arms:
            imgs.append(('minimal', 'disk', arch))
            imgs.append(('kde', 'disk', arch))
        logger.debug("expected images: %s", imgs)
        return tuple(imgs)

    @property
    def koji_done(self):
        """Rather slow way to check if Koji builds are done. Will
        return True if we have at least one task of each method and
        all tasks are in one of the known 'finished' states (CLOSED,
        CANCELED or ASSIGNED.)
        """
        opts = {'state': [], 'method': ('createLiveCD', 'createAppliance',
                                         'createImage')}
        tasks = self.get_koji_tasks(opts, nocache=True)
        if not tasks:
            logger.debug("koji_done: no tasks found")
            return False

        # KOJI: as we're trying to avoid using the koji module,
        # these values are hard-coded. Ideally we would use
        # koji.TASK_STATES here.
        if any(task['state'] not in (2, 3, 5) for task in tasks):
            logger.debug("koji_done: running task found")
            return False

        return True

    @property
    def pungi_done(self):
        """Check to see if Pungi has finished (by looking for the
        'finish' file in the compose log directory).
        """
        doneurl = "{0}/../logs/finish".format(self.https_url_generic)
        return fedfind.helpers.url_exists(doneurl)

    def _get_boot_url(self, arch):
        """Get the expected URL for the boot.iso of a given arch."""
        tmpl = '{0}/{1}/os/images/boot.iso'
        return tmpl.format(self.https_url_generic, arch)

    def get_koji_tasks(self, opts=None, nocache=False):
        """Query Koji for nightly tasks, and return a list of tasks.
        By default finds all live images. opts is an opts dict for the
        koji listTasks() method; the purpose of passing one from here
        is to specify the method and/or states we want to find images
        for. If nocache is True, any current cached result will be
        ignored, and the new result cached."""
        if not opts:
            opts = dict()
        # KOJI: as we're trying to avoid using the koji module, this
        # value is hard-coded. It means 'CLOSED'. Ideally we would use
        # koji.TASK_STATES['CLOSED'] here. We default to finding
        # completed tasks.
        if 'state' not in opts:
            opts['state'] = (2,)
        if 'method' not in opts:
            opts['method'] = ('createLiveCD',)
        elif isinstance(opts['method'], six.string_types):
            opts['method'] = (opts['method'],)
        for (key, value) in opts.items():
            if not value:
                del opts[key]

        # Check the cache. Thanks, StackOverflow, for the dict hash
        # trick: https://stackoverflow.com/questions/5884066
        # We could turn it into a tuple but then we have to run around
        # making sure none of the values are lists.
        key = json.dumps(opts, sort_keys=True)
        if not nocache and key in self._kojicache:
            return self._kojicache[key]

        # This is a little clever-clever fuzzy cache matching logic.
        # We're basically looking for cache entries which are super-
        # sets of the query. Then we'll filter down their results.
        if not nocache:
            cachekeys = self._kojicache.keys()
            for cachekey in cachekeys:
                cacheopts = json.loads(cachekey)
                if fedfind.helpers.cache_key_match(cacheopts, opts):
                    tasks = self._kojicache[cachekey]
                    for opt in ('state', 'method', 'arch'):
                        if opt in opts and opts[opt]:
                            tasks = [task for task in tasks if
                                     task[opt] in opts[opt]]
                    # cache the exact result so we don't go through
                    # this all again
                    self._kojicache[key] = tasks
                    return tasks

        client = fedfind.kojiclient.ClientSession(
            'http://koji.fedoraproject.org/kojihub')
        self._kojicache[key] = client.find_nightly_tasks(
            date=self._dateobj, release=self.release, opts=opts)
        return self._kojicache[key]

    def get_koji_images(
            self, methods=('createLiveCD', 'createAppliance', 'createImage'),
            arches=None):
        """Find all or some of our Koji nightly tasks, and return a
        list of fedfind.Image instances, one per task that produced
        images. Methods is an iterable of Koji task methods (each
        method requires another query, so we want to be able to limit
        this to as few methods as possible when we can).
        """
        client = fedfind.kojiclient.ClientSession(
            'http://koji.fedoraproject.org/kojihub')
        imgs = list()
        urls = list()
        opts = {'method': methods}
        if arches:
            opts['arch'] = list(arches)
        tasks = self.get_koji_tasks(opts)
        try:
            urls = client.find_task_images(tasks)
        except (fedfind.exceptions.NoImageError,
                fedfind.exceptions.NoFilesError):
            logger.warn("No Koji images found!")
        imgs.extend([self.image_from_url_or_path(url=url) for url in urls])
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
                if not any(term in query.terms
                           for term in ('disk', 'docker', 'vagrant')):
                    needdisk = False
            if query.attr == 'arch' and not query.neg and query.exact:
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

    @cached_property
    def previous_release(self):
        """The previous release for a RawhideNightly is always the
        previous day's RawhideNightly. Note this code is basically
        identical for BranchedNightly but it cannot be shared in the
        parent class because they have different signatures."""
        # This may raise a ValueError, but as that's what this is
        # supposed to do on failure anyway...no need to handle it at
        # all. Just let it raise.
        date = fedfind.helpers.date_check(self.compose)
        yday = date - datetime.timedelta(1)
        return self.__class__(yday)

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

    @cached_property
    def previous_release(self):
        """The previous release for a BranchedNightly is always the
        previous day's BranchedNightly. There is one case in which
        this is a lie: the very first BranchedNightly for any release.
        The answer we give will never exist, and the correct answer
        would be the previous day's RawhideNightly. However, there is
        really no sane way we can handle this case: we could check
        for the answer's existence and return RawhideNightly if it
        doesn't exist, but this would be slow and would only work for
        the couple of weeks that nightly releases are actually kept
        around.

        Note this code is basically identical for BranchedNightly but
        it cannot be shared in the parent class because they have
        different signatures."""
        try:
            date = fedfind.helpers.date_check(self.compose)
        except ValueError:
            return None
        yday = date - datetime.timedelta(1)
        return self.__class__(yday, self.release)

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
        self._prefurl = "mirror"

    @abc.abstractproperty
    def _rsyncpath(self):
        """Top level path for this release, relative to the fedora-
        buffet bundle in rsync (/pub on the master mirror).
        """
        pass

    @cached_property
    def all_images(self):
        """All images for this release."""
        return self.get_mirror_images(prefurl=self._prefurl)

    @cached_property
    def exists(self):
        """Release 'exists' if its top-level mirror path is there."""
        url = '{0}/{1}'.format(fedfind.const.RSYNC, self._rsyncpath)
        logger.debug("exists: checking URL %s", url)
        return fedfind.helpers.url_exists(url)

    @cached_property
    def koji_done(self):
        """For non-nightlies, we just assume Koji and Pungi are done
        if the compose exists.
        """
        return self.exists

    @cached_property
    def pungi_done(self):
        """For non-nightlies, we just assume Koji and Pungi are done
        if the compose exists.
        """
        return self.exists

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

        if self._prefurl == "direct":
            return tmpl.format(fedfind.const.HTTPS_DL, self._rsyncpath)
        else:
            return tmpl.format(fedfind.const.HTTPS, self._rsyncpath)

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. Getting this right for all historic releases would be a
        bit of a pain, so the stuff here is really only valid for F21+
        - but that's all we're likely to want to check anyway. For
        these releases, for the Intel arches we expect a Server DVD
        and netinst and Workstation and KDE live images, and for ARM
        (after it became a primary arch in F20) we expect a minimal
        and a KDE disk image (for F23+) or an Xfce disk image (for
        <F23). For Cloud we expect, er, FIXME?
        """
        imgs = list()
        intels = (arch.name for arch in fedfind.const.ARCHES if
                  arch.group == 'intel')
        arms = (arch.name for arch in fedfind.const.ARCHES if
                arch.group == 'arm')
        for arch in intels:
            imgs.append(('server', 'netinst', arch))
            imgs.append(('server', 'dvd', arch))
            imgs.append(('workstation', 'live', arch))
            imgs.append(('kde', 'live', arch))
        if int(self.release) > 19:
            for arch in arms:
                imgs.append(('minimal', 'disk', arch))
                if int(self.release) < 23:
                    imgs.append(('xfce', 'disk', arch))
                else:
                    imgs.append(('kde', 'disk', arch))
        return tuple(imgs)

    def get_mirror_images(self, prefurl=''):
        """Find images in the main mirror tree by parsing rsync output.
        This is about the simplest / most reliable method I could
        figure out for scraping the mirror tree. _rsyncpath is the path
        prefix to restrict the search to. prefurl is passed all the
        way through to Image.__init__() to let subclasses specify the
        preferred URL prefix for their images.
        """
        # This excludes files but includes directories (we have to
        # include directories to be able to include their contents)
        args = ['{0}/{1}/'.format(fedfind.const.RSYNC, self._rsyncpath),
                '--recursive', '--include=*/']
        # This includes files that end with one of our image
        # extensions
        args.extend(['--include=*{0}'.format(ext)
                     for ext in fedfind.const.IMAGE_EXTS])
        args.append('--exclude=*')
        logger.debug("get_mirror_images: rsync args: %s", args)
        null = open(os.devnull)
        (retcode, out) = fedfind.helpers.rsync_helper(args, True)
        if retcode:
            return []
        # This finds the output lines that are image files (ones
        # ending with our image extensions) and produces a URL by
        # combining the base alt URL with the file path, which is the
        # fifth field of the rsync output
        paths = ('{0}/{1}'.format(self._rsyncpath, o.split()[4])
                 for o in out.splitlines()
                 for e in fedfind.const.IMAGE_EXTS if o.endswith(e))
        return [self.image_from_url_or_path(path=path, prefurl=prefurl)
                for path in paths]


class Compose(MirrorRelease):
    """A TC/RC compose, stored in the staging tree."""
    def __init__(self, release, milestone, compose):
        super(Compose, self).__init__(
            release=release, milestone=milestone, compose=compose)
        # typical use of TC/RC images doesn't work well with the
        # download.fp.o redirector; the mirrors don't pick up
        # the images fast enough. Basically, things wanting to
        # download TC/RC images usually want to get them from dl.
        self._prefurl = "direct"

    @cached_property
    def previous_release(self):
        """For a TC/RC the previous release is usually just minus one
        from the number, but there are some tricky cases commented in
        the code. We will raise an error for RC1 / TC1. RC1.1 or TC3.2
        are handled, but not RC3.2.3 or RC4a because goddamnit, stop
        it."""
        num = self.compose.replace('TC', '').replace('RC', '')
        # I'm gonna handle one decimal place but no damn more.
        # Also, I am not proud of this. Good lord, no.
        if '.' in num:
            try:
                prev = Decimal(num) - Decimal('0.1')
            except InvalidOperation as err:
                raise ValueError(err)
            if int(prev) == prev:
                prev = str(int(prev))
            else:
                prev = str(prev)
            prev = self.compose.replace(num, prev)
            return self.__class__(self.release, self.milestone, prev)
        # If the 'compose' value is something odd, this int() call
        # will raise a ValueError...but that's what we'd want to do
        # on failure anyway, so let it raise.
        elif int(num) > 1:
            prev = str(int(num) - 1)
            prev = self.compose.replace(num, prev)
            return self.__class__(self.release, self.milestone, prev)
        elif 'TC' in self.compose:
            # This is a TC1. Here we're going to use a slight cheat
            # suggested by Peter Robinson: we're gonna return the
            # previous milestone release, which will always have
            # been the previous release candidate.
            milerel = Milestone(self.release, self.milestone)
            return milerel.previous_release
        else:
            # This is an RC1. We don't know how high the TC series
            # went. We *can* handle this case in one of two fairly
            # silly ways: get the milestone from wikitcms and find
            # the highest numbered TC compose event and return that
            # release, or we can just pick a number and start
            # bisecting from there ("Does TC10 exist? No? Try TC5.
            # Does that exist? Alright, try TC7..." and rinse and
            # repeat. But on the whole, I think I'm gonna wait for
            # composedb. We're using a custom exception so this
            # case is easy for tools to identify and post a helpful
            # error for.
            raise fedfind.exceptions.PreviousRC1Error

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

    @cached_property
    def previous_release(self):
        """We're only going to bother handling the current convention
        (Alpha, Beta, Final), otherwise we'd need a big list of the
        rules older releases followed and it's really not worth it.
        The result may well be a lie for an old release. For Alpha we
        return the previous stable release, not the previous Beta."""
        if self.milestone == 'Beta':
            return self.__class__(self.release, 'Alpha')
        elif self.milestone == 'Alpha':
            return get_release(str(int(self.release) - 1))

    @property
    def _rsyncpath(self):
        return 'fedora/linux/releases/test/{0}_{1}'.format(
            self.release, self.milestone)

## STABLE RELEASE CLASSES ##

class CurrentRelease(MirrorRelease):
    """A release that public mirrors are expected to carry (not an
    archived one).
    """
    def __init__(self, release):
        super(CurrentRelease, self).__init__(release=release)

    @cached_property
    def previous_release(self):
        """Always just the stable release numbered 1 lower, unless
        that's 0. Same for all stable releases, but sharing it
        between them is a bit of a pain. get_release() handles the
        0 case for us (and raises ValueError)."""
        return get_release(str(int(self.release) - 1))

    @property
    def _rsyncpath(self):
        return 'fedora/linux/releases/{0}'.format(self.release)

class ArchiveRelease(MirrorRelease):
    """An archived Fedora (post-Fedora Core) release."""
    def __init__(self, release):
        super(ArchiveRelease, self).__init__(release=release)

    @cached_property
    def previous_release(self):
        """Always just the stable release numbered 1 lower, unless
        that's 0. Same for all stable releases, but sharing it
        between them is a bit of a pain. get_release() handles the
        0 case for us (and raises ValueError)."""
        return get_release(str(int(self.release) - 1))

    @property
    def _rsyncpath(self):
        return 'archive/fedora/linux/releases/{0}'.format(self.release)


class CoreRelease(MirrorRelease):
    """A Fedora Core release."""
    def __init__(self, release):
        super(CoreRelease, self).__init__(release=release)

    @cached_property
    def previous_release(self):
        """Always just the stable release numbered 1 lower, unless
        that's 0. Same for all stable releases, but sharing it
        between them is a bit of a pain. get_release() handles the
        0 case for us (and raises ValueError)."""
        return get_release(str(int(self.release) - 1))

    @property
    def _rsyncpath(self):
        return 'archive/fedora/linux/core/{0}'.format(self.release)

## END STABLE RELEASE CLASSES ##
