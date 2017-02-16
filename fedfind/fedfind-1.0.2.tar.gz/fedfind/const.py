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
# This file defines various shared constants.

KOJI_BASE = 'https://kojipkgs.fedoraproject.org/work'
DISK_EXTS = ('.raw.xz', '.qcow2')
DOCKER_EXTS = ('.tar.gz',)
ISO_EXTS = ('.iso',)
IMAGE_EXTS = DISK_EXTS + DOCKER_EXTS + ISO_EXTS
NIGHTLY_BOOT_ARCHES = ('x86_64', 'i386', 'armhfp')
ARCHES = ('x86_64', 'i386', 'i686', 'armhfp', 'ppc', 'source')
RSYNC = 'rsync://dl.fedoraproject.org/fedora-buffet'
HTTPS = 'https://download.fedoraproject.org/pub'
KNOWN_PREFIXES = (RSYNC, HTTPS, 'http://download.fedoraproject.org/pub',
                  'https://dl.fedoraproject.org/pub',
                  'http://dl.fedoraproject.org/pub')
MASH_BASE = 'https://kojipkgs.fedoraproject.org/mash'

FLAVORS = dict(cloud = dict(names=('cloud',), subs=('base', 'atomic')),
               workstation = dict(names=('workstation',)),
               server = dict(names=('server',)))
LOADOUTS = dict(desktop = dict(names=('desktop',)),
                kde = dict(names=('kde',)),
                xfce = dict(names=('xfce',)),
                lxde = dict(names=('lxde',)),
                mate = dict(names=('mate_compiz', 'mate-compiz', 'mate')),
                soas = dict(names=('soas',)),
                design_suite = dict(names=('design_suite', 'design-suite')),
                electronic_lab = dict(names=('electronic_lab', 'electronic-lab')),
                games = dict(names=('games',)),
                jam_kde = dict(names=('jam_kde',)),
                robotics = dict(names=('robotics',)),
                scientific_kde = dict(names=('scientific_kde', 'scientific-kde')),
                security = dict(names=('security',)),
                minimal = dict(names=('minimal',)))
ISO_TYPES = ('dvd', 'live', 'netinst', 'disc1', 'disc2', 'disc3', 'disc4', 'disc5', 'disc6')
