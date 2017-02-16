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

"""Defines the Image class used to represent images."""

import fedfind.const
import fedfind.helpers


class Image(object):
    """A representation of a Fedora image. Must be given at least one
    of 'url' or 'path'. 'url' is an absolute URL to a Fedora image.
    'path' is a path relative to the top level of the Fedora mirror
    system - /pub on the master mirror - so if an instance has a 'path'
    attribute,
    https://mirrors.fedoraproject.org/mirrorlist?path=pub/(path)
    should work. If only 'path' is given, 'url' will be set to the
    URL for the image using the https://download.fedoraproject.org/
    redirector. If only 'url' is given, we will figure out 'path' only
    if the URL uses dl.fedoraproject or download.fedoraproject.

    url is used as the string representation, so the string for an
    Image instance should usually be a valid link to download it.

    If both 'url' and 'path' are passed, self.path and self.url will
    both be set, and on your own head be it if for some reason they're
    entirely different. I can't think of a good reason to do this.

    If given only 'url' and/or 'path', will attempt to figure out
    various attributes of the image. Most of the attributes can
    also be overridden at instantiation time, so if you know any of
    them for sure, you can just set them and avoid the guesswork.

    Really should be given a valid HTTPS URL or Fedora mirror system
    path. You may be able to get useful results in some sense by
    passing something else as url and/or path (e.g. a filesystem path)
    but it's not really expected. Can be used fairly independently of
    the rest of fedfind if you just want to use it to figure out some
    attributes of an arbitrary Fedora image.

    NOTE on datestamp vs. compose: for a typical nightly image, the
    date is 'compose', *NOT* 'datestamp'. 'datestamp' exists for the
    case where TC/RC images have a date stamp, which is sometimes the
    case for disk image builds. For 'version identification' purposes
    you usually want to use release, milestone, compose.
    """
    def __init__(self, url='', path='', arch='', imagetype='', flavor='',
                 subflavor='', loadout='', datestamp='', release='',
                 milestone='', compose='', prefurl=''):
        if not url and not path:
            raise TypeError("fedfind.Image() needs url or path.")
        self.arch = arch
        self.imagetype = imagetype
        self.flavor = flavor
        self.subflavor = subflavor
        self.loadout = loadout
        self.payload = ''
        self.datestamp = fedfind.helpers.date_check(
            datestamp, fail_raise=False, out='str')
        self.release = str(release).capitalize()
        self.milestone = str(milestone).capitalize()

        try:
            self.compose = fedfind.helpers.date_check(
                datestamp, fail_raise=True, out='str')
        except ValueError:
            self.compose = str(compose).upper()

        self.path = path
        if not path:
            for pfx in fedfind.const.KNOWN_PREFIXES:
                if url.startswith(pfx):
                    self.path = url.replace(pfx, '', 1)

        # If we have a mirror path, define various known URLs derived
        # from it.
        if self.path:
            self.mirror_url = '{0}/{1}'.format(fedfind.const.HTTPS, path)
            self.direct_url = '{0}/{1}'.format(fedfind.const.HTTPS_DL, path)
            self.rsync_url = '{0}/{1}'.format(fedfind.const.RSYNC, path)

        self.url = url
        if not url:
            if str(prefurl).lower() == 'mirror' and self.mirror_url:
                self.url = self.mirror_url
            elif str(prefurl).lower() == 'direct' and self.direct_url:
                self.url = self.direct_url
            elif str(prefurl).lower() == 'rsync' and self.rsync_url:
                self.url = self.rsync_url
            elif self.mirror_url:
            # Use the HTTPS URL which goes through the mirror redirect
            # system as the default URL.
                self.url = self.mirror_url
            elif self.direct_url:
                self.url = self.direct_url
            elif self.rsync_url:
                self.url=self.rsync_url

        self.filename = self.url.split('/')[-1]
        # Sort weight value for approx. how 'important' this image is
        self.weight = 0

        # attempt to figure out unspecified attributes.
        checkurl = self.url.lower()
        checkfile = self.filename.lower()

        if not self.imagetype:
            if checkfile == 'boot.iso':
                self.imagetype = 'boot'
            if any(checkfile.endswith(ext) for ext in fedfind.const.ISO_EXTS):
                for isotype in fedfind.const.ISO_TYPES:
                    if isotype in checkurl:
                        self.imagetype = isotype
            elif any(checkfile.endswith(ext)
                     for ext in fedfind.const.DISK_EXTS):
                self.imagetype = 'disk'
            elif any(checkfile.endswith(ext)
                     for ext in fedfind.const.FILESYSTEM_EXTS):
                self.imagetype = 'filesystem'

        if not self.flavor and not self.loadout:
            for flav in fedfind.const.FLAVORS:
                if any(val in checkurl for val in flav.values):
                    self.flavor = flav.name
                    self.weight = flav.weight
                    if flav.subs:
                        for sub in flav.subs:
                            if '{0}-{1}'.format(flav.name, sub) in checkurl:
                                self.subflavor = sub

        if not self.flavor and not self.loadout:
            for load in fedfind.const.LOADOUTS:
                if any(val in checkurl for val in load.values):
                    self.loadout = load.name
                    self.weight = load.weight

        if self.flavor:
            if self.subflavor:
                self.payload = '{0} {1}'.format(self.flavor, self.subflavor)
            else:
                self.payload = self.flavor
        elif self.loadout:
            self.payload = self.loadout

        # Try to identify 'generic' media
        if not self.payload and (self.imagetype == 'dvd' or
                                 self.imagetype == 'boot' or
                                 self.imagetype == 'netinst' or
                                 'disc' in self.imagetype):
            self.payload = 'generic'
            self.weight = 300

        # Handle live media without explicit 'Desktop' in the name
        if not self.payload and self.imagetype == 'live':
            self.payload = 'desktop'
            self.weight = 200

        if not self.arch:
            for arc in fedfind.const.ARCHES:
                if any(val in checkurl for val in arc.values):
                    self.arch = arc.name
                    self.weight += arc.weight

        elems = checkfile.split('.')[0].split('-')
        for elem in elems:
            # We want to capture the *first* matching element, to get
            # '21' not '5' for Fedora-Live-Workstation-x86_64-21-5.iso
            if (elem.isdigit() and
                    int(elem) in range(0, 100) and not
                    self.release):
                self.release = elem
            try:
                fedfind.helpers.date_check(elem, fail_raise=True, out='str')
                if not self.compose:
                    self.compose = elem
                elif not self.datestamp:
                    self.datestamp = elem
            except ValueError:
                pass

        # this will usually match the wikitcms 'version' concept, but
        # not always, significantly not for Rawhide nightlies. There's
        # a whole existential can o' worms there.
        self.version = self.release
        if self.milestone:
            self.version += ' {0}'.format(self.milestone)
        if self.compose:
            self.version += ' {0}'.format(self.compose)

    def __str__(self):
        return self.url

    def __repr__(self):
        return ("{0}(url='{1}', path='{2}', arch='{3}', imagetype='{4}', "
                "flavor='{5}', subflavor='{6}', loadout='{7}', "
                "datestamp='{8}', release='{9}', milestone='{10}', "
                "compose='{11}')").format(
                    self.__class__, self.url, self.path, self.arch,
                    self.imagetype, self.flavor, self.subflavor, self.loadout,
                    self.datestamp, self.release, self.milestone, self.compose)

    @property
    def desc(self):
        """A description of the image."""
        if self.arch:
            archtext = 'for {0}'.format(self.arch)
        else:
            archtext = ''
        return '{0} {1} image {2}'.format(
            self.payload, self.imagetype, archtext).strip()

    @property
    def exists(self):
        """Does the image in question actually exist? Try and access
        it and find out. If self.path is set it **MUST** be the path
        relative to the top level of the mirror system. If path is not
        set, url must be a complete https or rsync URL."""
        if self.path:
            rsync = '{0}/{1}'.format(fedfind.const.RSYNC, self.path)
            return fedfind.helpers.url_exists(rsync)
        return fedfind.helpers.url_exists(self.url)
