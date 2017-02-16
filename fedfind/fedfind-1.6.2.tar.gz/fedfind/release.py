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
import six
import time

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
    (current, archive, core...) for stable releases.

    Not all values are sanity checked; this may return a non-plausible
    release. Specifically, we do not check the sanity of milestone or
    compose values. An insane milestone value might be silently turned
    into a sane one, depending on other values; an insane compose
    value is likely to result in either an exception or a non-
    plausible release. Of course this function may also return a
    release that does not exist, and this is desired in some cases.

    Note that if all three values are left unset, you will get a
    RawhideNightly instance for today's date. Also note that either
    release or milestone being set to Rawhide will always result in
    a RawhideNightly; this is to ensure compatibility with wikitcms,
    where Rawhide compose events are versioned as e.g. 23 Rawhide
    20150304. Note that wikitcms similarly tries to handle fedfind
    release values (by guessing a release number for a version like
    Rawhide '' 20150304), so usually, fedfind and wikitcms versions
    are transparently interchangeable.

    For nightlies, pass compose as 'YYYYMMDD' or a datetime.date
    object. You'll wind up with either a RawhideNightly, Branched
    Nightly or PostRelease, depending on release and milestone. If
    you set a valid release number and leave milestone unset, you'll
    get a PostRelease only if it exists and BranchedNightly for the
    same values doesn't, otherwise you'll get BranchedNightly. If
    you set a valid release number and a valid nightly milestone,
    you'll get what you asked for. For any other case you'll wind up
    with a RawhideNightly. If you set a nightly-type milestone and
    leave compose unset, we will use today's date as the compose.

    For TCs/RCs, you must specify a valid milestone and compose. If
    you don't specify release, we'll try and find out what the
    current Branched is, and use that. If you don't specify a
    milestone, we'll raise ValueError.

    For milestone releases (Alpha/Beta), specify the milestone. We
    will guess the release in the same way as for TCs/RCs if it is not
    passed. Note that milestone 'Final' will be treated the same way
    as no milestone at all, i.e. returning a stable release.

    For stable releases, specify the release. You may specify
    milestone 'Final' but it is not necessary. There is no release
    guessing for stable releases.
    """
    # For safety in case these are passed as None.
    if not release:
        release = ''
    if not milestone:
        milestone = ''
    if not compose:
        compose = ''


    # UTILITY NESTED FUNCTIONS

    def not_or_str(values, strings):
        """True if all values are false-y or if any value contains any
        of the strings in the 'strings' iterable. Only used by guess_
        compose.
        """
        for val in values:
            if val and any(st == str(val).lower() for st in strings):
                return True
        if any(values):
            return False
        return True


    # NESTED FUNCTIONS FOR VALUE GUESSING

    def guess_compose(release='', milestone='', compose=''):
        """Works out what to use as 'compose' value. We never want
        to transform it if set, so simply returns it. If not set, we
        guess at the current date if 'release' and 'milestone' are
        not set, or set to one of the 'snapshot'-type values;
        otherwise we leave it blank (this is so e.g. (22, '', '')
        returns Fedora 22).
        """
        snaps = ('rawhide', 'branched', 'postrelease')
        if not compose and not_or_str((release, milestone), snaps):
            logger.debug("Guessing date")
            compose = datetime.date.today()
        return compose

    def guess_release(release='', milestone='', compose=''):
        """Works out what to use as a 'release' value. We handle a
        few different guessing scenarios here, and conversion from
        wikitcms '24 Rawhide (date)' type settings.
        """
        # Regardless of any other value, if milestone is Rawhide, we
        # return Rawhide. This is to correctly 'translate' wikitcms
        # 23 Rawhide 20150324 (for e.g.) to release 'Rawhide'.
        if milestone.lower() == 'rawhide':
            return 'Rawhide'

        # Aside from that, if release is set, sanity check and return
        # it.
        if release:
            check = str(release).lower()
            if check.isdigit() or check == 'rawhide':
                return release
            else:
                raise ValueError("get_release(): Release must be a number "
                                 "or Rawhide!")

        # If we were specifically asked for a valid milestone, return
        # appropriate release.
        if milestone.lower() == 'branched':
            return fedfind.helpers.get_current_release() + 1
        elif milestone.lower() == 'postrelease':
            return fedfind.helpers.get_current_release()

        # Otherwise, if compose is a date, guess Rawhide...
        elif fedfind.helpers.date_check(compose, fail_raise=False):
            return 'Rawhide'

        # ...otherwise, guess next release (to allow e.g. 'Beta TC2'
        # with no release).
        return fedfind.helpers.get_current_release() + 1


    # UTILITY FUNCTIONS FOR SELECTING APPROPRIATE CLASSES

    def get_stable(release):
        """Return the appropriate stable release class for a given
        release number.
        """
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

    def get_nightly(release, milestone, date):
        """Return the appropriate nightly release class for a given
        release, milestone, and date. Handles guessing the milestone.
        """
        if milestone.lower() == 'postrelease':
            return PostRelease(release=release, compose=date)
        elif milestone.lower() == 'branched':
            return BranchedNightly(release=release, compose=date)
        else:
            if milestone:
                logger.warn("Invalid milestone %s for nightly! Ignoring.",
                            milestone)
            # Guess: try Branched, if it doesn't exist, try PR
            branched = BranchedNightly(release=release, compose=date)
            if branched.exists:
                return branched
            else:
                pr = PostRelease(release=release, compose=date)
                if pr.exists:
                    return pr
                else:
                    return branched


    # ACTUAL LOGIC STARTS HERE

    compose = guess_compose(release, milestone, compose)
    release = guess_release(release, milestone, compose)

    # All Rawhide cases.
    if release == 'Rawhide':
        if not fedfind.helpers.date_check(compose, fail_raise=False):
            raise ValueError("get_release(): for Rawhide, compose must be "
                             "a date!")
        return RawhideNightly(compose)

    # All nightly cases.
    date = fedfind.helpers.date_check(compose, fail_raise=False)
    if date:
        return get_nightly(release, milestone, date)

    # TCs/RCs.
    if milestone and compose:
        return Compose(release, milestone, compose)

    # At this point we've handled all composes that we can. If compose
    # is still set, this has to be an error.
    if compose:
        raise ValueError("get_release(): cannot guess milestone for non-date "
                         "compose!")

    # Non-final milestones.
    if milestone and str(milestone) != 'Final':
        return Milestone(release, milestone)

    # Anything that makes it this far must be a stable release.
    return get_stable(release)


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
        iterable of (payload, imagetype, imagesubtype, arch) tuples;
        imagesubtype may be empty (i.e. it's optional). Here we list
        ones that most releases share; Release classes should start
        from this list and add more. For Fedora.next releases (post
        F20), we expect KDE and Workstation lives and Cloud base and
        atomic disk images. For Fedora 7-20 we expect KDE and Desktop
        lives. For releases after ARM became primary (F20+), we expect
        a minimal disk image and one desktop disk image; for F20-F22
        it was Xfce, for F23+ it's KDE.

        Getting this historically correct is a bit anal, but if
        nothing else this code may serve as some kind of record of
        Fedora key deliverables for the future.
        """
        imgs = list()
        intels = (arch.name for arch in fedfind.const.ARCHES if
                  arch.group == 'intel')
        arms = (arch.name for arch in fedfind.const.ARCHES if
                arch.group == 'arm')
        for arch in intels:
            if self.release.lower() == 'rawhide' or int(self.release) > 20:
                imgs.append(('kde', 'live', '', arch))
                imgs.append(('workstation', 'live', '', arch))
                imgs.append(('cloud', 'disk', 'raw', arch))
                # per dgilmore, Atomic has always been x86_64 only
                if arch == 'x86_64':
                    imgs.append(('cloud_atomic', 'disk', 'raw', arch))
            elif int(self.release) > 6:
                imgs.append(('kde', 'live', '', arch))
                imgs.append(('desktop', 'live', '', arch))

        if self.release.lower() == 'rawhide' or int(self.release) > 19:
            for arch in arms:
                imgs.append(('minimal', 'disk', 'raw', arch))
                if self.release.isdigit() and int(self.release) > 22:
                    imgs.append(('xfce', 'disk', 'raw', arch))
                else:
                    imgs.append(('kde', 'disk', 'raw', arch))

        return imgs

    @abc.abstractproperty
    def koji_done(self):
        """Whether all Koji tasks for the compose are complete."""
        pass

    @abc.abstractproperty
    def pungi_done(self):
        """Whether all Pungi tasks for the compose are complete."""
        pass

    def wait(self, waittime=480, delay=120, retries=5):
        """Wait up to 'time' minutes for the compose to be complete,
        checking every 'delay' seconds. If a query raises exception,
        retry up to 'retries' times (with an increasing amount of time
        between retries) before giving up. Returns when the compose
        appears, raises an exception in all other cases. Raises
        WaitError when the time expires. May raise an IOError via
        url_exists if a query fails many times. Eventually will raise
        any other exception hit by a query, if retries don't help."""
        logger.debug("Waiting up to %s mins for compose", str(waittime))
        waitstart = time.time()
        # for error handling, see 'except' clause below
        errs = 0
        errtime = 60
        while True:
            if time.time() - waitstart > waittime * 60:
                raise fedfind.exceptions.WaitError("Waited too long")
            logger.debug("Checking for compose...")
            try:
                if self.pungi_done and self.koji_done:
                    logger.debug("Compose complete!")
                    return
                else:
                    time.sleep(delay)
                # Reset the error counter and sleep timer, cos we succeeded.
                errs = 0
                errtime = 60
            except Exception as err:
                # We want to be somewhat fault-tolerant if anything errors
                # while we're waiting. First we try again immediately, then
                # we try several delayed retries before finally giving up.
                logger.debug("Caught exception while waiting! %s", err)
                errs += 1
                if errs == 1:
                    continue
                elif errs <= retries:
                    logger.debug("Sleeping %s to make errors go away",
                                 str(errtime))
                    time.sleep(errtime)
                    errtime += errtime
                    continue
                else:
                    raise

    def difference(self, other):
        """Similarly to the behaviour of the set.difference() method,
        this tells you which images exist for this release but not
        for other. Returns a set of (payload, imagetype, imagesubtype,
        arch) tuples identifying the unique images. 'other' must be
        another Release instance (you may often want to use
        self.previous_release).
        """
        ours = set(
            (img.payload, img.imagetype, img.imagesubtype,
             img.arch) for img in self.all_images)
        theirs = set(
            (img.payload, img.imagetype, img.imagesubtype,
             img.arch) for img in other.all_images)
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
        logger.debug("expected images: %s", self.expected_images)
        missing = set()
        for (payload, imagetype, sub, arch) in self.expected_images:
            queries = [
                Query('payload', payload),
                Query('imagetype', imagetype),
                Query('arch', arch),
            ]
            if sub:
                queries.append(Query('imagesubtype', sub))
            # This is a bit of a hack, but we happen to know that
            # we'll need to check basically all the images, and for
            # nightlies it's actually slower to use the 'optimised'
            # method in this case because it doesn't cache all its
            # results
            res = self._query_images(queries)
            if res:
                logger.debug('check_expected: found %s', res)
            else:
                missing.add((payload, imagetype, sub, arch))
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
        is. For a nightly release, beyond the universal images, we
        expect a generic boot ISO for Intel arches.
        """
        imgs = super(Nightly, self).expected_images
        intels = (arch.name for arch in fedfind.const.ARCHES if
                  arch.group == 'intel')
        for arch in intels:
            imgs.append(('generic', 'boot', '', arch))
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
        is. Beyond the universal images, for Fedora.next releases
        (F21+), we expect Server netinst and DVD images. Otherwise,
        for post-FC1 releases we expect a generic boot image, and for
        post-FC2 releases we expect a generic DVD image. For all
        releases up to F14 we expect at least one CD (CDs were dropped
        with F15).
        """
        imgs = super(MirrorRelease, self).expected_images
        intels = (arch.name for arch in fedfind.const.ARCHES if
                  arch.group == 'intel')
        for arch in intels:
            if self.release.lower() == 'rawhide' or int(self.release) > 20:
                imgs.append(('server', 'netinst', '', arch))
                imgs.append(('server', 'dvd', '', arch))
            elif int(self.release) > 1:
                imgs.append(('generic', 'boot', '', arch))
                if int(self.release) > 2:
                    imgs.append(('generic', 'dvd', '', arch))
                # 7 and 8 had no installer CDs, for...some reason?
                if int(self.release) < 15 and int(self.release) not in (7, 8):
                    imgs.append(('generic', 'disc', '', arch))
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


class PostRelease(MirrorRelease):
    """A post-release nightly for a stable release. These are slightly
    odd ducks that for now have only Atomic images built; they're part
    of https://fedoraproject.org/wiki/Changes/Two_Week_Atomic , the
    idea is to provide regularly rebuilt Atomic base images. They more
    or less look like TC/RC releases.
    """
    def __init__(self, release, compose):
        super(PostRelease, self).__init__(
            release=release, milestone='Postrelease', compose=compose)
        # As with TCs/RCs, mirror system is not usually fast enough
        # for these.
        self._prefurl = "direct"

    @cached_property
    def previous_release(self):
        """The previous release for a PostRelease is always the
        previous day's PostRelease. There is one case in which
        this is a lie: the very first PostRelease for any release.
        The answer we give will never exist, and the correct answer
        would be the stable release. Catching this is a bit tricky,
        though.

        Note this code is basically identical for the Nightlies but
        it cannot be shared in the parent class because they have
        different signatures."""
        try:
            date = fedfind.helpers.date_check(self.compose)
        except ValueError:
            return None
        yday = date - datetime.timedelta(1)
        return self.__class__(self.release, yday)

    @property
    def _rsyncpath(self):
        return 'alt/atomic/testing/{0}-{1}'.format(self.release, self.compose)

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. These nightlies are pretty odd, and only Cloud images are
        built, so we do not take the 'universal' definition from the
        Release class, but we do 'expect' some non-blocking images,
        because I think people interested in these nightlies probably
        want to make sure all the Cloud images built.
        """
        return (
            ('cloud', 'disk', 'raw', 'x86_64'),
            ('cloud', 'vagrant', 'libvirt', 'x86_64'),
            ('cloud', 'vagrant', 'virtualbox', 'x86_64'),
            ('cloud', 'docker', '', 'x86_64'),
            ('cloud_atomic', 'canned', '', 'x86_64'))

    @property
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
        subdirectories are named for primary arches and contain
        .treeinfo files, and where the 'generic' network install
        image for the release was built from). The only installer
        tree in these nightlies is the Cloud_Atomic one, so we'll
        have to return that, it's not a very good choice though.
        """
        return '{0}/{1}/Cloud_Atomic'.format(fedfind.const.HTTPS_DL,
                                             self._rsyncpath)

    @property
    def pungi_done(self):
        """FIXME: This is kind of a gross hack, but it should work
        for now. It's just pure magic knowledge: I happen to know that
        when this directory exists, the compose process is done.
         https://pagure.io/releng/pull-request/22 is what we need
        to do this better.
        """
        url = '{0}/{1}/Cloud-Images'.format(fedfind.const.HTTPS_DL,
                                            self._rsyncpath)
        return fedfind.helpers.url_exists(url)

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
