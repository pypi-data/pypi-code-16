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

"""Various shared constants."""

import collections

# For both of these, we identify each we want to consider unique;
# that is the 'name'. 'values' is an iterable of values which should
# map to that name; for instance, we don't want to treat i486, i586
# and i686 as separate arches, but every time we see any of those we
# want to treat it as i386. 'weight' is an integer to be used for
# sort weighting if desired.
#
# For ArchTuple, each entry in ARCHES is a primary arch. group is used
# to group related arches together. current is whether it's currently
# a primary arch.
#
# For LoadTuple, each entry in FLAVORS or LOADOUTS is something we
# consider a unique flavor or loadout. subs is an iterable of sub-
# flavors.
ArchTuple = collections.namedtuple('ArchTuple',
                                   'name values group weight current')
LoadTuple = collections.namedtuple('LoadTuple', 'name values subs weight')

KOJI_BASE = 'https://kojipkgs.fedoraproject.org/work'
RSYNC = 'rsync://dl.fedoraproject.org/fedora-buffet'
HTTPS = 'https://download.fedoraproject.org/pub'
HTTPS_DL = 'https://dl.fedoraproject.org/pub'
KNOWN_PREFIXES = (RSYNC, HTTPS, 'http://download.fedoraproject.org/pub',
                  HTTPS_DL, 'http://dl.fedoraproject.org/pub')
MASH_BASE = 'https://kojipkgs.fedoraproject.org/mash'

DISK_EXTS = ('.raw.xz', '.qcow2')
VAGRANT_EXTS = ('.box',)
FILESYSTEM_EXTS = ('.tar.gz', '.tar.xz')
ISO_EXTS = ('.iso',)
IMAGE_EXTS = DISK_EXTS + FILESYSTEM_EXTS + VAGRANT_EXTS + ISO_EXTS
# 'cloud_atomic' are ISO images with Cloud_Atomic in their name, which
# are for some sort of installer-based Atomic deployment method:
# http://blog.theforeman.org/2015/06/unattended-deployments-of-fedora-and.html
# If more of this kind of image turns up we'll have to come up with a
# generic name and make this more complex somehow...
ISO_TYPES = ('dvd', 'live', 'netinst', 'disc1', 'disc2', 'disc3', 'disc4',
             'disc5', 'disc6', 'disc7', 'rescuecd', 'cloud_atomic')

ARCHES = (
    ArchTuple('x86_64', ('x86_64',), 'intel', 2000, True),
    ArchTuple('i386', ('i386', 'i486', 'i586', 'i686'), 'intel', 2000, True),
    ArchTuple('armhfp', ('armhfp',), 'arm', 1000, True),
    ArchTuple('ppc', ('ppc',), 'ppc', 1000, False),
    ArchTuple('ppc64', ('ppc64',), 'ppc', 1000, False))

FLAVORS = (
    LoadTuple('cloud', ('cloud',), ('base', 'atomic'), 200),
    LoadTuple('workstation', ('workstation',), (), 220),
    LoadTuple('server', ('server',), (), 210))

# This has to be ordered so we get the right result for e.g. 'kde'
# vs. 'jam_kde'
LOADOUTS = (
    LoadTuple('desktop', ('desktop',), (), 200),
    LoadTuple('kde', ('kde',), (), 190),
    LoadTuple('xfce', ('xfce',), (), 80),
    LoadTuple('soas', ('soas',), (), 73),
    LoadTuple('mate', ('mate_compiz', 'mate-compiz', 'mate'), (), 72),
    LoadTuple('cinnamon', ('cinnamon',), (), 71),
    LoadTuple('lxde', ('lxde',), (), 70),
    LoadTuple('design_suite', ('design_suite', 'design-suite'), (), 60),
    LoadTuple('electronic_lab', ('electronic_lab', 'electronic-lab'), (), 60),
    LoadTuple('games', ('games',), (), 60),
    LoadTuple('robotics', ('robotics',), (), 60),
    LoadTuple('security', ('security',), (), 60),
    LoadTuple('jam_kde', ('jam_kde',), (), 60),
    LoadTuple('scientific_kde', ('scientific_kde', 'scientific-kde'), (), 60),
    LoadTuple('minimal', ('minimal',), (), 90),
    # When Docker gets more supported we should bump it up to ~KDE weight
    LoadTuple('docker', ('docker',), (), 55),
    LoadTuple('source', ('source',), (), 50))
