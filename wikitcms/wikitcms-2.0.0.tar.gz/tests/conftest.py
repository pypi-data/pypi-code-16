# Copyright (C) 2015 Red Hat
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

import pytest

@pytest.fixture(scope="module")
def hard_sort_releases():
    """Some cases only tuple sort can handle (not string sort)."""
    return [
        ('9', 'Beta', 'RC1'),
        ('10', 'Alpha', 'TC1'),
        ('10', 'Alpha', 'TC2'),
        ('10', 'Alpha', 'TC10'),
    ]

@pytest.fixture(scope="module")
def old_releases():
    """Oddball version triplets from old releases."""
    return [
        ('12', 'Alpha', 'TCRegression'),
        ('12', 'Beta', 'PreBeta'),
        ('12', 'Beta', 'TC'),
        ('12', 'Final', 'Pre-RC'),
        ('12', 'Final', 'RC1'),
        ('21', 'Rawhide', '2014 06'),
        ('21', 'Nightly', '2014 08'),
        ('21', 'Alpha', 'TC1'),
    ]

@pytest.fixture(scope="module")
def standard_releases():
    """Anything should be able to sort these."""
    return [
        ('22', 'Final', 'RC1'),
        ('22', 'Postrelease', '20151015'),
        ('23', 'Rawhide', '20150607'),
        ('23', 'Branched', '20150717'),
        ('23', 'Alpha', 'TC1'),
        ('23', 'Alpha', 'TC2'),
        ('23', 'Alpha', 'RC1'),
        ('23', 'Beta', 'TC1'),
        ('23', 'Beta', 'TC2'),
        ('23', 'Final', 'RC1'),
        ('23', 'Final', 'RC1.1'),
    ]
