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

from __future__ import unicode_literals
from __future__ import print_function

import collections

# For all of these, we identify each we want to consider unique; that
# is the 'name'. 'values' is an iterable of values which should map to
# that name; for instance, we don't want to treat i486, i586 and i686
# as separate arches, but every time we see any of those we want to
# treat it as i386. 'weight' is an integer to be used for sort
# weighting if desired.
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
LoadTuple = collections.namedtuple('LoadTuple', 'name values weight')


RSYNC = 'rsync://dl.fedoraproject.org/fedora-buffet'
HTTPS = 'https://download.fedoraproject.org/pub'
HTTPS_DL = 'https://dl.fedoraproject.org/pub'
KNOWN_PREFIXES = (RSYNC, HTTPS, 'http://download.fedoraproject.org/pub',
                  HTTPS_DL, 'http://dl.fedoraproject.org/pub')
NIGHTLY_BASE = 'https://kojipkgs.fedoraproject.org/compose'
PDC_API = 'https://pdc.fedoraproject.org/rest_api/v1'

# we could import these from pungi but jeez, the dependencies are
# growing as it is. Pungi compose states.
PUNGI_SUCCESS = ("FINISHED", "FINISHED_INCOMPLETE")
PUNGI_FAILURE = ("DOOMED",)
PUNGI_DONE = PUNGI_SUCCESS + PUNGI_FAILURE

# PAYLOADS
# This has to be ordered so we get the right result for e.g. 'kde'
# vs. 'jam_kde'
PAYLOADS = (
    LoadTuple('Desktop', ('desktop',), 200),
    LoadTuple('KDE', ('kde',), 190),
    LoadTuple('Xfce', ('xfce',), 80),
    LoadTuple('SoaS', ('soas',), 73),
    LoadTuple('MATE', ('mate_compiz', 'mate-compiz', 'mate'), 72),
    LoadTuple('Cinnamon', ('cinnamon',), 71),
    LoadTuple('LXDE', ('lxde',), 70),
    LoadTuple('Design_suite', ('design_suite', 'design-suite'), 60),
    LoadTuple('Electronic_lab', ('electronic_lab', 'electronic-lab'), 60),
    LoadTuple('Games', ('games',), 60),
    LoadTuple('Robotics', ('robotics',), 60),
    LoadTuple('Security', ('security',), 60),
    LoadTuple('Jam_KDE', ('jam_kde',), 60),
    LoadTuple('Scientific_KDE', ('scientific_kde', 'scientific-kde'), 60),
    LoadTuple('Astronomy_KDE', ('astronomy_kde',), 60),
    LoadTuple('Minimal', ('minimal',), 90),
    LoadTuple('Source', ('source', 'srpms'), 50),
    LoadTuple('Cloud', ('cloud', 'docker-base'), 200),
    LoadTuple('Atomic', ('atomic',), 200),
    LoadTuple('Workstation', ('workstation',), 220),
    LoadTuple('Server', ('server',), 210),
    LoadTuple('Everything', ('everything',), 210)
)


# ARCHES
ARCHES = (
    ArchTuple('x86_64', ('x86_64',), 'intel', 2000, True),
    ArchTuple('i386', ('i386', 'i486', 'i586', 'i686'), 'intel', 2000, True),
    ArchTuple('armhfp', ('armhfp',), 'arm', 1000, True),
    ArchTuple('ppc', ('ppc',), 'ppc', 1000, False),
    ArchTuple('ppc64', ('ppc64',), 'ppc', 1000, False))
