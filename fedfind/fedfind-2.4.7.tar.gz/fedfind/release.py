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
from __future__ import unicode_literals
from __future__ import print_function

import abc
import datetime
import logging
import re
import string

from collections import defaultdict
# this was used for TC/RC handling, we may still need it again
#from decimal import (Decimal, InvalidOperation)
from functools import partial

from cached_property import cached_property
from productmd.images import SUPPORTED_IMAGE_FORMATS
from productmd.composeinfo import get_date_type_respin

import fedfind.const
import fedfind.exceptions
import fedfind.helpers

logger = logging.getLogger(__name__)


def get_release_url(url):
    """Get a release based on its location. This is mostly intended
    for Pungi 4, but PostRelease is also handled for awful practical
    reasons. This is conceptually more or less the *inverse* of the
    various logics we have for finding where composes are based on
    their identities: the class we instantiate immediately does the
    exact opposite of this operation to re-constitute the URL. If we
    wind up keeping this around very long we should improve that mess
    somehow.
    """
    return get_release(url=url)

def get_release_cid(cid):
    """Get a release by compose ID. I am sad that this is necessary,
    but it is. This will always return the 'raw', non-mirrored compose
    location, use get_release() or get_release_label() to get mirrored
    composes.
    """
    return get_release(cid=cid)

def get_release(release='', milestone='', compose='', respin=None,
                cid='', label='', url='', promote=False):
    """Function to return an appropriate Release subclass for the
    version information. Figures out if you want a nightly, compose,
    milestone, or stable release and gives it to you. Catches some
    nonsense choices. Tries to figure out the appropriate subclass
    (current, archive, core...) for stable releases. Can work off
    fedfind/wikitcms-style 'release, milestone, compose, respin',
    or from a compose URL (expected to be the URL available from
    releng fedmsgs - the /compose directory of a Pungi 4 compose, or
    the top level of a two-week Atomic compose), or from a Pungi 4
    compose ID, or from a Pungi 4 compose label. Yeah, that's a lot
    of choice.

    Priority goes to url, then label, then cid, then r/m/c/r. So if
    url is specified, all other values are ignored; if url is not
    specified but label is, label is used and all other values except
    release are ignored; if neither url nor label is specified but
    cid is, cid is used and all other values are ignored; if none of
    url, label, or cid is specified, we do what we can with whatever
    release, milestone, compose and respin values are given. Note
    if you pass label you probably also want to pass release; labels
    identify only milestone and compose. If you don't, it will be
    guessed. By default, if you pass 'cid', we do not try to 'promote'
    the result - that is, if the compose in question is a production
    compose and was actually synced out as a Candidate or released as
    a Milestone or a stable release, we do not discover its label and
    give you one of those instances based on the label, you just get
    a Production, which is the compose's expected location in the non-
    mirrored kojipkgs server where *all* Pungi 4 composes initially
    appear. If you want to 'promote' from the cid in this way, pass
    promote=True.

    Not all values are sanity checked; this may return a non-plausible
    release. Specifically, we do not check the sanity of milestone or
    compose values. An insane milestone value might be silently turned
    into a sane one, depending on other values; an insane compose
    value is likely to result in either an exception or a non-
    plausible release. Of course this function may also return a
    release that does not exist, and this is desired in some cases.

    Note that if all four values are left unset, you will get the
    current date's most recent RawhideNightly if there is one, or
    else you will get a non-existent RawhideNightly for today's date
    with respin 0. Also note that either release or milestone being
    set to Rawhide will always result in a RawhideNightly; this is to
    ensure compatibility with wikitcms, where Rawhide compose events
    are versioned as e.g. 23 Rawhide 20150304. Wikitcms similarly
    tries to handle fedfind release values (by guessing a release
    number for a version like Rawhide '' 20150304 0), so usually,
    fedfind and wikitcms versions are transparently interchangeable.

    For nightlies, pass compose as 'YYYYMMDD'. You'll wind up with
    either a RawhideNightly, BranchedNightly or PostRelease,
    depending on release and milestone. If you set a valid release
    number and leave milestone unset, you'll get a PostRelease only if
    it exists and BranchedNightly for the same values doesn't,
    otherwise you'll get BranchedNightly. If you set a valid release
    number and a valid nightly milestone, you'll get what you asked
    for. For any other case you'll wind up with a RawhideNightly. If
    you set a nightly-type milestone and leave compose unset, we will
    use today's date as the compose. For all cases, if you specify
    respin, you'll get an instance with that respin, whether it exists
    or not. If you don't specify it, fedfind will try to find the
    latest completed compose for the release, milestone and date given
    or guessed and return that; if there aren't any, it will return
    an instance for 'respin 0' for that date.

    For TCs/RCs, you must specify a valid milestone and compose. If
    you don't specify release, we'll try and find out what the
    current Branched is, and use that. If you don't specify a
    milestone, we'll raise ValueError.

    For milestone releases (Alpha/Beta), specify the milestone. We
    will guess the release in the same way as for TCs/RCs if it is not
    passed. Note that milestone 'Final' will be treated the same way
    as no milestone at all, i.e. returning a stable release.

    As things stand right now, TCs/RCs and Alpha/Beta releases are
    not actually handled, as Fedora has not yet decided how to handle
    these with Pungi 4, so the expected classes are entirely missing
    and any attempt to instantiate them this way or any other way will
    fail. This will be resolved once we've figured out how these
    composes will actually be produced and versioned under Pungi 4.

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
        snaps = ('rawhide', 'branched', 'postrelease', 'production')
        if not compose and not_or_str((release, milestone), snaps):
            logger.debug("Guessing date")
            compose = fedfind.helpers.date_check(
                datetime.date.today(), out='str')
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
        if milestone.lower() in ('branched', 'production'):
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
        # we'll need to change a bit when we get to archived P4
        # releases...
        if int(release) > 23:
            return Pungi4Mirror(
                '/fedora/linux/releases/{0}'.format(str(release)))
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

    def guess_postrelease_respin(release, date):
        """We have to handle 'respins' for nightlies if one wasn't
        explicitly passed. For postreleases we just count down from
        5 and stop when one exists or we hit 0.
        """
        respin = 5
        while respin > -1:
            test = PostRelease(release=release, compose=date, respin=respin)
            if test.exists:
                return test
            respin -= 1
        return test

    def guess_nightly_respin(release, date):
        """Mostly like above, only we check something different."""
        if release == 'Rawhide':
            testcls = partial(RawhideNightly, compose=date)
        else:
            testcls = partial(BranchedNightly, release=release, compose=date)
        respin = 5
        while respin > -1:
            test = testcls(respin=respin)
            if test.status in fedfind.const.PUNGI_SUCCESS:
                return test
            respin -= 1
        return test

    def get_nightly(release, milestone, date, respin=None):
        """Return the appropriate nightly release class for a given
        release, milestone, date, and respin. Handles guessing the
        milestone. If respin is not specified, handles guessing that.
        """
        if milestone.lower() == 'production':
            if respin is None:
                raise ValueError("Cannot guess respin for a production "
                                 "candidate compose!")
            return Production(release, date, respin)

        if milestone.lower() == 'postrelease':
            if respin is not None:
                return PostRelease(
                    release=release, compose=date, respin=respin)
            else:
                return guess_postrelease_respin(release, date)

        elif milestone.lower() == 'branched':
            if respin is not None:
                return BranchedNightly(
                    release=release, compose=date, respin=respin)
            else:
                return guess_nightly_respin(release, date)

        else:
            if milestone:
                logger.warn("Invalid milestone %s for nightly! Ignoring.",
                            milestone)
            # Guess: try Branched, if it doesn't exist, try PR. We
            # don't include 'production' in guessing.
            if respin is not None:
                branched = BranchedNightly(release=release, compose=date,
                                           respin=respin)
            else:
                branched = guess_nightly_respin(release, date)
            if branched.exists:
                return branched
            else:
                if respin is not None:
                    prel = PostRelease(
                        release=release, compose=date, respin=respin)
                else:
                    prel = guess_postrelease_respin(release, date)
                if prel.exists:
                    return prel
                else:
                    return branched

    def parse_label(label):
        """Produce a milestone/compose/respin tuple from a compose label."""
        (milestone, comp) = label.split('-')
        (compose, respin) = comp.split('.')
        return (milestone, compose, int(respin))

    def parse_cid(cid):
        """Produce a release/milestone/compose/respin tuple from a
        compose ID. Will always give the values that produce a raw,
        non-mirrored Release instance.
        """
        # Handle 2 Week Atomic 'compose ID' (the openQA BUILD, same as
        # the directory name)
        atomicpatt = re.compile(r'(\d+)-(\d{8,8})\.?(\d+)?')
        match = atomicpatt.match(cid)
        if match:
            respin = '0'
            if match.group(3):
                respin = match.group(3)
            return (match.group(1), 'Postrelease', match.group(2), respin)

        # otherwise, assume a real Pungi 4 compose ID
        (release, date, typ, respin) = fedfind.helpers.parse_cid(cid)
        if typ == 'nightly':
            if release == 'rawhide':
                milestone = ''
                release = 'Rawhide'
            else:
                milestone = 'Branched'
            return (release, milestone, date, int(respin))
        elif typ == 'production':
            return (release, 'Production', date, int(respin))
        else:
            raise ValueError("get_release(): could not parse compose ID "
                             "{0}!".format(cid))

    def parse_url(url):
        """Handle a URL if specified. If it's a two-week Atomic URL,
        return an appropriate release/milestone/compose/respin set.
        If we can find a compose ID in it, return r/m/c/r again.
        Otherwise just return None.
        """
        # This is what PostReleases look like.
        atomicpatt = re.compile(r'.*atomic/testing/(.*)-(\d{8,8})\.?(\d+)?/?')
        match = atomicpatt.match(url)
        if match:
            respin = '0'
            if match.group(3):
                respin = match.group(3)
            return (match.group(1), 'Postrelease', match.group(2), respin)
        else:
            cid = fedfind.helpers.find_cid(url)
            if cid:
                try:
                    return parse_cid(cid)
                except ValueError:
                    # let's fall through to a Pungi4Release
                    pass
        return None

    # ACTUAL LOGIC STARTS HERE
    if url:
        ret = parse_url(url)
        if ret:
            (release, milestone, compose, respin) = ret
        else:
            # we couldn't parse the URL, so just give a raw Pungi4
            # Release and hope for the best.
            return Pungi4Release(url)
    elif cid:
        (release, milestone, compose, respin) = parse_cid(cid)
        if promote:
            label = fedfind.helpers.label_from_cid(cid)
            if label:
                (milestone, compose, respin) = parse_label(label)
    elif label:
        (milestone, compose, respin) = parse_label(label)

    compose = guess_compose(release, milestone, compose)
    release = guess_release(release, milestone, compose)

    if respin is None and '.' in compose:
        # as a bit of fudge, we'll see if we got a compose value that
        # looks like it includes a respin, and parse it out if so.
        # This will handle '1.1' and '20160314.n.0'
        elems = compose.split('.')
        (compose, respin) = (elems[0], elems[-1])

    if respin is not None:
        try:
            respin = int(str(respin))
        except ValueError:
            raise ValueError("get_release(): respin must be an integer!")

    # All Rawhide cases.
    if release == 'Rawhide':
        if not fedfind.helpers.date_check(compose, fail_raise=False):
            raise ValueError("get_release(): for Rawhide, compose must be "
                             "a date!")
        if respin is not None:
            return RawhideNightly(compose, respin)
        else:
            return guess_nightly_respin(release, compose)

    # All nightly cases. 'Production' also handled here, as 'compose'
    # is a date.
    if fedfind.helpers.date_check(compose, fail_raise=False):
        return get_nightly(release, milestone, compose, respin)

    # Production candidates ('Alpha 1.1' etc.)
    if milestone and compose:
        if respin is None:
            raise ValueError("get_release(): for candidate composes, respin "
                             "must be specified or included in compose")
        # first, see if we have a Compose - i.e. the compose has been
        # synced to alt/stage
        rel = Compose(release, milestone, compose, respin)
        if rel.exists:
            return rel

        # if not, try getting the cid from the label and return a
        # Production - the location for the compose on the unmirrored
        # kojipkgs server
        if not label:
            label = "{0}-{1}.{2}".format(milestone, compose, respin)
        if not cid:
            # We may actually have a compose ID already on one path:
            # if the user called us with a compose ID and promote=True
            # and we got a label, but the compose is not mirrored and
            # so not found as a Compose above. Re-use it in this case.
            cid = fedfind.helpers.cid_from_label(release, label)
        if cid:
            (release, milestone, compose, respin) = parse_cid(cid)
            return Production(release, compose, respin)
        else:
            raise ValueError("get_release(): could not find release for {0}, "
                             "{1}, {2}".format(release, milestone, compose))

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


class Release(object):
    """Abstract class for releases, providing shared attributes and
    methods.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, release='', milestone='', compose=''):
        self.release = str(release).capitalize()
        self.milestone = str(milestone).capitalize()
        self.compose = str(compose).upper()
        self.version = self.release
        if self.milestone:
            self.version += ' {0}'.format(self.milestone)
        if self.compose:
            self.version += ' {0}'.format(self.compose)
        try:
            if self.respin:
                self.version += '.{0}'.format(self.respin)
        except AttributeError:
            # some classes have no respin
            pass
        # hack up a productmd-style compose ID. PostRelease overrides
        # this, so it's only used for stable releases; we'll just use
        # the correct format with a placeholder date. The 'type'
        # indicator is omitted for 'production' composes in productmd,
        # and the 'respin' counter is optional.
        self.cid = "Fedora-{0}-19700101".format(self.release)

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
    def exists(self):
        """Whether the release is considered to 'exist'."""
        pass

    @abc.abstractproperty
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
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
        iterable of (subvariant, imagetype, arch) tuples. Here we list
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
                imgs.append(('kde', 'live', arch))
                imgs.append(('workstation', 'live', arch))
                imgs.append(('cloud_base', 'raw-xz', arch))
                # per dgilmore, Atomic has always been x86_64 only
                if arch == 'x86_64':
                    imgs.append(('atomic', 'raw-xz', arch))
            elif int(self.release) > 6:
                imgs.append(('kde', 'live', arch))
                imgs.append(('desktop', 'live', arch))

        if self.release.lower() == 'rawhide' or int(self.release) > 19:
            for arch in arms:
                imgs.append(('minimal', 'raw-xz', arch))
                if self.release.isdigit() and int(self.release) > 22:
                    imgs.append(('xfce', 'raw-xz', arch))
                else:
                    imgs.append(('kde', 'raw-xz', arch))

        return imgs

    @abc.abstractproperty
    def done(self):
        """Whether the compose is complete."""
        pass

    @abc.abstractproperty
    def metadata(self):
        """dict containing some productmd-style metadata for the
        compose. For a compose that actually exists, it's expected to
        contain at least the key 'images', whose value should be a
        dict in the form of the productmd images.json file. May also
        contain 'composeinfo' and 'rpms' items containing dicts in
        those formats (though 'rpms' is very large and should
        probably be retrieved / parsed only on specific request).
        For a compose that doesn't exist, this dict may be empty.
        """
        pass

    @property
    def all_images(self):
        """All images from the compose. Flatten the image dicts from
        the compose metadata, stuff the variant into each image dict,
        and return the list.
        """
        if not self.metadata['images']:
            return []
        images = []
        imgsdict = self.metadata['images']['payload']['images']
        for variant in imgsdict.keys():
            for arch in imgsdict[variant].keys():
                for imgdict in imgsdict[variant][arch]:
                    imgdict['variant'] = variant
                    images.append(imgdict)
        return images

    def check_expected(self):
        """This checks whether all expected images are included in the
        release. If the release doesn't exist, it will raise an
        exception. If any expected images are missing, it will return
        a set of (subvariant, imagetype, arch) tuples identifying the
        missing images. If nothing is missing, it will return an empty
        set.
        """
        if not self.exists:
            raise ValueError('Release does not exist!')
        logger.debug("expected images: %s", self.expected_images)
        missing = set(self.expected_images)
        for exptup in self.expected_images:
            for imgdict in self.all_images:
                imgtup = (imgdict['subvariant'].lower(), imgdict['type'],
                          imgdict['arch'])
                if imgtup == exptup:
                    missing.discard(exptup)
        return missing

    def get_package_nvras(self, packages):
        """Passed a list of source package names, returns a dict with
        the names as the keys and the NVRAs of those packages found in
        the compose's tree as the values. May raise an exception if
        the compose doesn't exist, or it can't reach the server. For
        any package not found, the value will be the empty string.
        Note this truly returns NVRAs, not NEVRAs; we cannot discover
        the epoch. It returns the arch even though it's *always* going
        to be 'src' so you can feed the result to hawkey.split_nevra()
        """
        verdict = dict((package, '') for package in packages)
        initials = set([p[0].lower() for p in packages])
        text = ''
        # Grab the directory indexes we need. This is a bit different
        # for older releases; it's awkward to express this via the
        # classes so just conditionalize it here. Before F17, package
        # directories like this one are not split into subdirectories
        # by first character. Before F7, there was no /Everything.
        # Before F5, there was no /source.
        split = True
        if int(self.release) < 17:
            split = False
        if int(self.release) > 23:
            url = '{0}/Everything/source/tree/Packages/'.format(self.location)
        elif int(self.release) > 6:
            url = '{0}/Everything/source/SRPMS/'.format(self.location)
        elif int(self.release) > 4:
            url = '{0}/source/SRPMS/'.format(self.location)
        else:
            url = '{0}/SRPMS/'.format(self.location)
        if split:
            for i in initials:
                suburl = '{0}{1}/'.format(url, i)
                index = fedfind.helpers.urlopen_retries(suburl)
                text += index.read()
        else:
            text = fedfind.helpers.urlopen_retries(url).read()
            for line in text.splitlines():
                if 'anaconda' in line:
                    print(line)
        # Now find each package's NVR. This is making a couple of
        # assumptions about how the index HTML source will look and
        # also assuming that the 'version-release' is the bit after
        # packagename- and before .src.rpm, it's not perfect (won't do
        # epochs) but should be good enough.
        for package in packages:
            patt = re.compile('href="(' + package + r'.*?\.src)\.rpm')
            match = patt.search(text)
            if match:
                ver = match.group(1)
                verdict[package] = ver
        return verdict


class Pungi4Release(Release):
    """A Pungi 4 release. Real metadata! Other unicorn-like things! We
    *can* derive pretty much all information about a Pungi 4 release
    from its metadata, and this class works that way, and must be told
    where the compose is located: the single required argument is an
    HTTP(S) URL to the /compose directory for the compose. There are
    several optional args which will be stored on the instance (thus
    preventing those properties being retrieved from metadata) if set.
    Child classes may work more like old fedfind classes, allowing you
    to locate a compose based on its version information, and will
    pass the optional args. A Pungi4Release instance for a compose
    that does not exist at all is fairly useless and you will rarely
    want such a beast.
    """
    def __init__(self, location, release=None, milestone=None, compose=None,
                 respin=None, typ=None, cid=None, label=None, version=None):
        # _checkloc is used for finding metadata, checking existence,
        # stuff like that. 'location' is used for constructing public
        # URLs. the distinction is so Pungi4Mirror can have dl.fp.o
        # in _checkloc but download.fp.o in location.
        self.location = self._checkloc = location.strip('/')
        # These are defaults for semi-cached properties.
        self._status = None
        self._exists = False
        self._metadata = None
        self._release = release
        self._milestone = milestone
        self._compose = compose
        self._respin = respin
        self._type = typ
        self._cid = cid
        self._label = label
        self._version = version
        self._prefurl = "direct"

    def __repr__(self):
        return "{0}(location='{1}')".format(self.__class__, self.location)

    def __str__(self):
        return "{0} {1}".format(self.__class__.__name__, self.location)

    @property
    def exists(self):
        """Whether the compose exists. We cache 'True' because if we
        exist we're unlikely to *stop* existing."""
        if self._exists:
            return self._exists
        elif fedfind.helpers.url_exists(self._checkloc):
            self._exists = True
            return self._exists
        else:
            return False

    @cached_property
    def https_url_generic(self):
        """Everything tree is 'generic' for Pungi 4."""
        return "{0}/{1}".format(self.location, "/Everything")

    @property
    def status(self):
        """The canary file is all we need. We cache finished states as
        they will not change.
        """
        if self._status:
            return self._status
        if self.exists:
            try:
                url = self._checkloc[:-7] + "STATUS"
                resp = fedfind.helpers.urlopen_retries(url)
                resp = resp.read().decode('utf-8').strip('\n')
                if resp in fedfind.const.PUNGI_DONE:
                    self._status = resp
                return resp
            except ValueError:
                logger.warning("Pungi4Release: failed to find status!")
                return ""
        else:
            return ""

    @property
    def done(self):
        """Check status against the Pungi status constants.
        """
        return self.status in fedfind.const.PUNGI_DONE

    @property
    def metadata(self):
        """Read metadata from server. We cache this if we're done as
        it will not change.
        """
        done = self.done
        metadata = {'composeinfo': {}, 'images': {}}
        if done and self._metadata:
            return self._metadata
        elif self.exists:
            try:
                url = "{0}{1}".format(
                    self._checkloc, "/metadata/composeinfo.json")
                metadata['composeinfo'] = fedfind.helpers.download_json(url)
                url = "{0}{1}".format(self._checkloc, "/metadata/images.json")
                metadata['images'] = fedfind.helpers.download_json(url)
                if done:
                    self._metadata = metadata
                return metadata
            except ValueError:
                logger.error("Pungi4Release: failed to download metadata!")
                return metadata
        else:
            return metadata

    @property
    def cid(self):
        """Compose ID. It's a property because it may involve a remote
        trip. There are two places where this may be found (as for
        status), we check both.
        """
        try:
            return self.metadata['composeinfo']['payload']['compose']['id']
        except KeyError:
            if self._cid:
                return self._cid
            try:
                url = self._checkloc[:-7] + "COMPOSE_ID"
                resp = fedfind.helpers.urlopen_retries(url)
                resp = resp.read().decode('utf-8').strip('\n')
                self._cid = resp
                return resp
            except ValueError:
                logger.warning("Pungi4Release: failed to find compose ID!")
                return ""

    @property
    def label(self):
        """Compose 'label'. Exists only for production composes, looks
        like "Alpha-1.1" or similar. Found similarly to CID.
        """
        if self._label:
            return self._label
        try:
            return self.metadata['composeinfo']['payload']['compose']['label']
        except KeyError:
            logger.debug("Pungi4Release: failed to find compose label!")
            return ""

    @property
    def version(self):
        """For generic Pungi 4 release just use the CID stripped a bit.
        """
        if self._version:
            return self._version
        return self.cid.replace("Fedora-", "")

    @property
    def release(self):
        """Release. It's a property because it may involve a remote
        trip. _release is so subclasses for which this is intrinsic
        can define it and this property returns it.
        """
        if self._release:
            return self._release
        return self.cid.split('-')[1]

    @property
    def milestone(self):
        """Milestone. It's a property because it may involve a remote
        trip. _milestone is for same reasons as _release, above.
        """
        if self._milestone is not None:
            return self._milestone
        if self.label:
            return self.label.rsplit('-', 1)[0]
        else:
            # sometimes we just don't know
            return ''

    @property
    def compose(self):
        """Compose. It's a property because it may involve a remote
        trip. _milestone is for same reasons as _release, above.
        """
        if self._compose:
            return self._compose
        if self.label:
            return self.label.rsplit('-', 1)[1].split('.')[0]
        else:
            # sometimes we just don't know
            return ''

    @property
    def type(self):
        """Compose "type" (in productmd terms). Can be parsed from
        cid, but we prefer to read it from metadata. _type is for same
        reasons as _release, above.
        """
        if self._type:
            return self._type
        try:
            return self.metadata['composeinfo']['payload']['compose']['type']
        except KeyError:
            try:
                res = get_date_type_respin(self.cid)[1]
                if res:
                    return res
                else:
                    return ''
            except ValueError:
                return ''

    @property
    def respin(self):
        """Compose "respin" (in productmd terms). Can be parsed from
        cid, but we prefer to read it from metadata. _respin is for the
        same reasons as _release and _type, above.
        """
        if self._respin is not None:
            return self._respin
        if self.label:
            return self.label.rsplit('-', 1)[1].split('.')[1]
        try:
            return str(
                self.metadata['composeinfo']['payload']['compose']['respin'])
        except KeyError:
            try:
                res = get_date_type_respin(self.cid)[2]
                if res:
                    return str(res)
                else:
                    return ''
            except ValueError:
                return ''

    @property
    def expected_images(self):
        """See abstract class docstring for information on what this
        is. Beyond the universal images, we expect Server netinst and
        DVD images.
        """
        imgs = super(Pungi4Release, self).expected_images
        intels = (arch.name for arch in fedfind.const.ARCHES if
                  arch.group == 'intel')
        for arch in intels:
            imgs.append(('server', 'boot', arch))
            imgs.append(('server', 'dvd', arch))
        return tuple(imgs)

    @property
    def previous_release(self):
        """For Pungi 4 composes, we use PDC. We ask for all composes
        for the same release and type, find the one we 'are', and
        return the previous one. We can only do this for completed
        composes, because PDC only stores those. May raise ValueError
        on unknown problems and IndexError if this is the first
        compose of its type for the release.
        """
        if self.status not in fedfind.const.PUNGI_SUCCESS:
            raise ValueError("Cannot find previous compose for "
                             "incomplete or failed Pungi 4 compose!")
        params = {'version': self.release}
        # you can query 'releases' in PDC and releases have a property
        # which is a list of composes ordered by creation date. handy!
        pdcrel = fedfind.helpers.pdc_query('releases', params)[0]
        complist = pdcrel['compose_set']
        # filter to composes of the correct type
        complist = [comp for comp in complist if
                    get_date_type_respin(comp)[1] == self.type]
        try:
            idx = complist.index(self.cid)
        except IndexError:
            raise ValueError("Could not find previous compose for "
                             "{0}".format(self))
        if idx == 0:
            raise IndexError("{0} is the first compose of its type for this "
                             "release!".format(self))
        return get_release_cid(complist[idx-1])

#    def get_package_nvras(self, packages):
#        """Passed a list of package names, returns a dict with the
#        names as the keys and the NEVRAs of those packages found in
#        the compose's tree as the values. We use PDC for Pungi 4
#        composes; this might raise ValueError if contacting PDC fails.
#        The value for any package not found will be the empty string.
#        Note that unlike the generic version in the Release class used
#        for non-Pungi 4 releases, this gives NEVRAs, not NVRAs: we can
#        get the epoch from PDC. This allows more accurate comparisons,
#        but be careful if comparing a Pungi 4 vs. a non-Pungi 4.
#        """
#        print(self.cid)
#        verdict = dict((package, '') for package in packages)
#        params = [('compose', self.cid), ('arch', 'src')]
#        for package in packages:
#            params.append(('name', package))
#        res = fedfind.helpers.pdc_query('rpms', params)
#        for pkg in res:
#            verdict[pkg['name']] = pkg['srpm_nevra']
#        return verdict

## PUNGI 4 NIGHTLY CLASSES ##


class RawhideNightly(Pungi4Release):
    """Rawhide "nightly" (bit of a misnomer, now) composes."""
    def __init__(self, compose, respin=0):
        compose = str(compose)
        respin = str(respin)
        path = "rawhide/Fedora-Rawhide-{0}.n.{1}/compose".format(
            compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(RawhideNightly, self).__init__(
            url, release="Rawhide", milestone='', compose=compose,
            respin=respin, typ="nightly")


class BranchedNightly(Pungi4Release):
    """Branched "nightly" (bit of a misnomer, now) composes."""
    def __init__(self, release, compose, respin=0):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "branched/Fedora-{0}-{1}.n.{2}/compose".format(
            release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(BranchedNightly, self).__init__(
            url, release=release, milestone="Branched", compose=compose,
            respin=respin, typ="nightly")
        self._release = release
        self._milestone = "Branched"

## PUNGI 4 CANDIDATE COMPOSES ##


class Production(Pungi4Release):
    """A Pungi 4 'production' compose, on kojipkgs, identified by date
    and respin (not label). 'compose' is the date. e.g. 24, 20160314,
    1 for
    https://kojipkgs.fedoraproject.org/compose/24/Fedora-24-20160314.1
    The *same* compose may have been synced to the mirror system and
    be instantiable as a Compose (see below).
    NOTE: Production instances have their *real* milestone, compose
    and respin as self.milestone, self.compose, and self.respin, not
    'Production', the date, and the respin relative to date. This is
    is pretty much arbitrary.
    """
    def __init__(self, release, compose, respin):
        release = str(release)
        compose = str(compose)
        respin = str(respin)
        path = "{0}/Fedora-{0}-{1}.{2}/compose".format(
            release, compose, respin)
        url = '/'.join((fedfind.const.NIGHTLY_BASE, path))
        super(Production, self).__init__(url, release=release)
        # We do not set compose or milestone as we want those to be
        # parsed from the label - see class docstring.

    @property
    def version(self):
        """Use release milestone compose.respin, but don't set
        _version in init as that would cause remote trips, do it here
        as a property.
        """
        return "{0} {1} {2}.{3}".format(
            self.release, self.milestone, self.compose, self.respin)


class Compose(Pungi4Release):
    """A candidate compose that has been synced to the staging tree
    on the mirrors. The exact same compose may be available from
    kojipkgs as a Production (above). As for old-fedfind, we do not
    use the mirror system for this class because syncing is not super
    reliable (as I write this, a day after F24 Alpha 1.5 happened,
    mirrors.kernel.org has still not synced it fully). That's why this
    isn't a Pungi4Mirror subclass.
    """
    def __init__(self, release, milestone, compose, respin):
        release = str(release)
        milestone = str(milestone)
        compose = str(compose)
        respin = str(respin)
        label = "{0}-{1}.{2}".format(milestone, compose, respin)
        version = "{0} {1} {2}.{3}".format(release, milestone, compose, respin)
        url = '{0}/alt/stage/{1}_{2}'.format(
            fedfind.const.HTTPS_DL, release, label)
        super(Compose, self).__init__(
            url, release=release, milestone=milestone, compose=compose,
            respin=respin, label=label, typ="production", version=version)

    @property
    def status(self):
        """Assume mirrored composes are always FINISHED."""
        return "FINISHED"

## PUNGI 4 MIRROR CLASSES ##


class Pungi4Mirror(Pungi4Release):
    """A Pungi 4-type release which is in the mirror system (and thus
    rsync-able and mirror-able). We want to use dl.fp.o for grabbing
    metadata and stuff (as the mirror system is not sufficiently
    reliable) but print URLs with download.fp.o. We could use rsync
    for the 'exists' check but it's not really significantly better
    than using HTTP so let's not bother. Note, we do not actually have
    any of these yet, this is all theory-code.
    """
    def __init__(self, path, **kwargs):
        self._rsyncpath = path.rstrip('/')
        super(Pungi4Mirror, self).__init__("{0}{1}".format(
            fedfind.const.HTTPS_DL, path), **kwargs)
        self.location = "{0}{1}".format(fedfind.const.HTTPS, path)

    def __repr__(self):
        return "{0}(path='{1}')".format(self.__class__, self._rsyncpath)

    def __str__(self):
        return "{0} {1}".format(self.__class__.__name__, self._rsyncpath)

    @property
    def status(self):
        """Assume mirrored composes are always FINISHED."""
        return "FINISHED"

## NON-PUNGI 4 CLASSES ##


class MirrorRelease(Release):
    """A parent class for non-Pungi 4 releases. The name is a hangover
    from the pre-Pungi 4 world. This is fine. This is fine."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, release, milestone='', compose=''):
        super(MirrorRelease, self).__init__(release, milestone, compose)
        self._prefurl = "mirror"
        # Defaults for semi-cached properties.
        self._exists = False
        self._all_paths = []

    @abc.abstractproperty
    def _rsyncpath(self):
        """Top level path for this release, relative to the fedora-
        buffet bundle in rsync (/pub on the master mirror).
        """
        pass

    @property
    def all_paths(self):
        """All image paths for this release by parsing rsync output.
        This is about the simplest / most reliable method I could
        figure out for scraping the mirror tree. We use _rsyncpath
        to restrict the search.
        """
        if self._all_paths:
            return self._all_paths

        # This excludes files but includes directories (we have to
        # include directories to be able to include their contents)
        args = ['{0}/{1}/'.format(fedfind.const.RSYNC, self._rsyncpath),
                '--recursive', '--include=*/']
        # This includes files that end with one of our image
        # extensions
        args.extend(['--include=*{0}'.format(ext)
                     for ext in SUPPORTED_IMAGE_FORMATS])
        args.append('--exclude=*')
        logger.debug("get_mirror_paths: rsync args: %s", args)
        (retcode, out) = fedfind.helpers.rsync_helper(args, True)
        if retcode:
            return []
        # This finds the output lines that are image files (ones
        # ending with our image extensions) and returns their paths
        ret = [o.split()[4] for o in out.splitlines()
               for e in SUPPORTED_IMAGE_FORMATS
               if o.endswith(".{0}".format(e))]
        if ret:
            # if we got anything, we probably exist and can cache.
            self._all_paths = ret
        return ret

    @property
    def exists(self):
        """Release 'exists' if its top-level mirror path is there.
        True is cached as it will not change."""
        if self._exists:
            return self._exists
        # I used to use rsync, but it seems to be constantly full
        # lately (2016-02), so let's use http...
        url = '{0}/{1}'.format(fedfind.const.HTTPS_DL, self._rsyncpath)
        logger.debug("exists: checking URL %s", url)
        if fedfind.helpers.url_exists(url):
            self._exists = True
            return self._exists
        else:
            return False

    @property
    def done(self):
        """For non-nightlies, we just assume we're done if the compose
        exists.
        """
        return self.exists

    @property
    def location(self):
        """This is for partial compatibility with Pungi 4-style
        composes.
        """
        if self._prefurl == "direct":
            return "{0}/{1}".format(fedfind.const.HTTPS_DL, self._rsyncpath)
        else:
            return "{0}/{1}".format(fedfind.const.HTTPS, self._rsyncpath)

    @property
    def https_url_generic(self):
        """HTTPS URL for the 'generic' tree for this release (whose
        subdirectories are named for primary arches and contain
        .treeinfo files, and where the 'generic' network install
        image for the release was built from).
        """
        if int(self.release) < 7:
            return self.location
        elif int(self.release) < 21:
            return '{0}/Fedora'.format(self.location)
        elif int(self.release) >= 21:
            return '{0}/Server'.format(self.location)

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
                imgs.append(('server', 'netinst', arch))
                imgs.append(('server', 'dvd', arch))
            elif int(self.release) > 1:
                imgs.append(('everything', 'boot', arch))
                if int(self.release) > 2:
                    imgs.append(('everything', 'dvd', arch))
                # 7 and 8 had no installer CDs, for...some reason?
                if int(self.release) < 15 and int(self.release) not in (7, 8):
                    imgs.append(('everything', 'cd', arch))
        return tuple(imgs)

    @property
    def metadata(self):
        """Produce Pungi 4 / productmd-style metadata by analyzing the
        compose's properties. The result can be used in exactly the
        same way as you can access the *real* metadata for a Pungi 4
        compose, so you can treat non-Pungi 4 composes just the same.
        It's a long way from perfect, so far, but it's better than a
        slap around the face with a wet fish. This also helps us with
        internal stuff, like the way all_images is produced from this
        'metadata'.
        """
        imagesdict = defaultdict(lambda: defaultdict(list))
        for path in self.all_paths:
            imgdict = fedfind.helpers.create_image_dict(path)
            # this is kinda dumb, but as it happens, if the first
            # letter in the path is upper-case, we know that first
            # path element is the variant.
            if path[0] in string.ascii_uppercase:
                variant = path.split('/')[0]
            else:
                variant = "Fedora"
            imagesdict[variant][imgdict['arch']].append(imgdict)

        if isinstance(self, PostRelease):
            typ = "nightly"
        else:
            typ = "production"
        fullimgdict = {
            'header': {
                "version": "99",
            },
            'payload': {
                "compose": {
                    "id": self.cid,
                    "type": typ,
                },
                "images": imagesdict,
            },
        }
        return {'images': fullimgdict}


class Milestone(MirrorRelease):
    """A milestone release - Alpha or Beta. These are in fact built
    with Pungi 4, but the metadata for them is not shipped, so for now
    we just handle them as non-Pungi 4 composes (this code is exactly
    as it was in fedfind 1.6.2 in fact). Ideally we should be able to
    reconstruct a lot of the metadata from PDC instead of resorting to
    old-fashioned mirror scraping and synthesis, but I don't have the
    time to write all that right now. This at least will let people
    find the ISOs.
    """
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


class PostRelease(MirrorRelease):
    """A two-week Atomic testing compose. These get done nightly, not
    (yet) with Pungi 4, and contain only Atomic images. They more
    or less look like pre-Pungi 4 TC/RC releases.
    """
    def __init__(self, release, compose, respin=0):
        self.respin = str(respin)
        super(PostRelease, self).__init__(
            release=release, milestone='Postrelease', compose=compose)
        # As with TCs/RCs, mirror system is not usually fast enough
        # for these.
        self._prefurl = "direct"
        # Pungi 4-style compose ID. This is pretty 'correct' as all
        # the concepts match. We mark this as a 'nightly'.
        self.cid = "Fedora-{0}-{1}.n.{2}".format(
            self.release, self.compose, self.respin)


    @cached_property
    def previous_release(self):
        """There are sometimes respins of these composes. My best
        approximation here is to take the highest numbered respin from
        the previous day, on the assumption that respins are only done
        when something was seriously wrong (so a previous compose from
        the same day will never be something we want to deal with, and
        the final respin on a given day is probably the 'real' compose
        for that day). There is one case we can't handle very well:
        the very first PostRelease for any release.
        The answer we give will never exist, and the correct answer
        would be the stable release. Catching this is a bit tricky,
        though.
        """
        try:
            date = fedfind.helpers.date_check(self.compose, out='obj')
        except ValueError:
            return None
        yday = date - datetime.timedelta(1)
        yday = fedfind.helpers.date_check(yday, out='str')
        # annoyingly, we have stuff like 'only respin 0 and 2 exist'
        # (e.g. 23-20160217), we can't rely on just counting up till
        # we hit a respin that doesn't exist. Highest I've seen is
        # 3, so let's start at 5 and count down from there. This is
        # wasteful, but what're ya gonna do.
        test = self.__class__(self.release, yday, 5)
        while not test.exists and int(test.respin) > 0:
            test = self.__class__(self.release, yday, test.respin-1)
        return test

    @property
    def _rsyncpath(self):
        path = 'alt/atomic/testing/{0}-{1}'.format(self.release, self.compose)
        if int(self.respin):
            path = '{0}.{1}'.format(path, self.respin)
        return path

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
            ('cloud_base', 'raw-xz', 'x86_64'),
            ('cloud_base', 'vagrant-libvirt', 'x86_64'),
            ('cloud_base', 'vagrant-virtualbox', 'x86_64'),
            ('atomic', 'raw-xz', 'x86_64'),
            ('atomic', 'vagrant-libvirt', 'x86_64'),
            ('atomic', 'vagrant-virtualbox', 'x86_64'),
            ('docker_base', 'docker', 'x86_64'),
            ('atomic', 'boot', 'x86_64'))

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
    def done(self):
        """FIXME: This is kind of a gross hack, but it should work
        for now. It's just pure magic knowledge: I happen to know that
        when this directory exists, the compose process is done.
         https://pagure.io/releng/pull-request/22 is what we need
        to do this better.
        """
        url = '{0}/{1}/Cloud-Images'.format(fedfind.const.HTTPS_DL,
                                            self._rsyncpath)
        return fedfind.helpers.url_exists(url)

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
