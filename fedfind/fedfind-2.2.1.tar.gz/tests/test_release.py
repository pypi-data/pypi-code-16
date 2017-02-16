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

"""Tests for release.py."""

import datetime
import pytest

import mock
import fedfind.release

class FakeRelease(object):
    """Release stub used for testing nightly respin guessing. Gives
    the magic 'good' values for exists and status if respin is 3.
    """
    def __init__(self, *args, respin='', **kwargs):
        self.exists = False
        self.status = 'DOOMED'
        self.respin = respin
        if respin == 3:
            self.exists = True
            self.status = 'FINISHED'

class TestRelease:
    """Tests for release.py."""

    def test_get_release_offline(self):
        """Offline tests for get_release."""
        datestr = datetime.date.today().strftime('%Y%m%d')
        rels = (
            # Archive stable.
            ((15, '', '', None), (fedfind.release.ArchiveRelease, '15')),
            # Fedora Core stable (release string).
            (('6', '', '', None), (fedfind.release.CoreRelease, '6')),
            # 'Final' treated as stable.
            (('6', 'Final', '', None), (fedfind.release.CoreRelease, '6')),
            # Milestone. FIXME: disabled till we know how these will be with Pungi 4.
            #((23, 'Beta', ''), (fedfind.release.Milestone, '23', 'Beta')),
            # TC/RC. FIXME: disabled till we know how these will be with Pungi 4.
            #((23, 'Beta', 'RC1'), (fedfind.release.Compose, '23', 'Beta', 'RC1')),
            # Post-release stable nightly (date string).
            ((22, 'Postrelease', datestr, 0), (fedfind.release.PostRelease, '22', 'Postrelease', datestr, '0')),
            # Branched nightly.
            ((23, 'Branched', datestr, 1), (fedfind.release.BranchedNightly, '23', 'Branched', datestr, '1')),
            # Rawhide nightly.
            (('Rawhide', '', datestr, 2), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr, '2')),
            # Wikitcms format Rawhide.
            (('24', 'Rawhide', '{0}.n.0'.format(datestr), None),
             (fedfind.release.RawhideNightly, 'Rawhide', '', datestr, '0')),
            # OFFLINE GUESSES
            # Date guesses.
            ((23, 'Branched', '', 0), (fedfind.release.BranchedNightly, '23', 'Branched', datestr, '0')),
            (('Rawhide', '', '', 0), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr, '0')),
            ((22, 'Postrelease', '', 0), (fedfind.release.PostRelease, '22', 'Postrelease', datestr, '0')),
            # Default, check None is handled.
            ((None, None, None, 0), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr, '0')),
        )

        # Test that various get_release() invocations return expected
        # classes and values. Each rel's first tuple is the release,
        # milestone, compose values to pass to get_release. Its second
        # tuple's first value is always the expected class. The next
        # three values of the second tuple are optional, and they are
        # the expected release, milestone and compose; each will be
        # checked if present.
        for ((release, milestone, compose, respin), expected) in rels:
            got = fedfind.release.get_release(release, milestone, compose, respin)
            if not isinstance(got, expected[0]):
                pytest.fail("Testing {0} {1} {2} got class {3}".format(
                    release, milestone, compose, got.__class__))
            if len(expected) > 1:
                if not got.release == expected[1]:
                    pytest.fail("Testing {0} {1} {2} got release {3}".format(
                        release, milestone, compose, got.release))
            if len(expected) > 2:
                if not got.milestone == expected[2]:
                    pytest.fail("Testing {0} {1} {2} got milestone {3}".format(
                        release, milestone, compose, got.milestone))
            if len(expected) > 3:
                if not got.compose == expected[3]:
                    pytest.fail("Testing {0} {1} {2} got compose {3}".format(
                        release, milestone, compose, got.compose))
            if len(expected) > 4:
                if not got.respin == expected[4]:
                    pytest.fail("Testing {0} {1} {2} {3} got respin {4}".format(
                        release, milestone, compose, respin, got.respin))

        # Sanity check tests.
        with pytest.raises(ValueError):
            fedfind.release.get_release('foobar')

        with pytest.raises(ValueError):
            fedfind.release.get_release('23', '', 'RC2')

    @mock.patch('fedfind.release.Production.label', 'Alpha-1.1')
    def test_get_release_production(self):
        ret = fedfind.release.get_release(24, 'Production', '20160314', 0)
        assert isinstance(ret, fedfind.release.Production)
        assert ret.release == '24'
        assert ret.milestone == 'Alpha'
        assert ret.compose == '1'
        assert ret.respin == '1'

    @mock.patch('fedfind.release.ArchiveRelease.exists', False)
    def test_get_stable_current(self):
        ret = fedfind.release.get_release(23)
        assert isinstance(ret, fedfind.release.CurrentRelease)
        assert ret.release == '23'

    @mock.patch('fedfind.release.ArchiveRelease.exists', True)
    def test_get_stable_archive(self):
        # NOTE: this test is intended to hit the code which checks
        # whether an ArchiveRelease exists and returns it if so; the
        # tested number has to be greater than the cutoff which just
        # returns an ArchiveRelease without checking
        ret = fedfind.release.get_release(23)
        assert isinstance(ret, fedfind.release.ArchiveRelease)
        assert ret.release == '23'

    @mock.patch('fedfind.helpers.get_current_release', return_value=23)
    def test_get_release_guess_release(self, fakecurrent):
        # Release guessing. We can't test this very hard or we'd have
        # to keep updating the tests all the goddamned time, or the
        # test would duplicate the logic of get_current_release and
        # that seems pointless. But we can at least check it's not
        # crashing and returns the right class.
        datestr = datetime.date.today().strftime('%Y%m%d')

        got = fedfind.release.get_release('', 'Branched', '', 0)
        assert isinstance(got, fedfind.release.BranchedNightly)
        assert got.compose == datestr
        assert got.release == '24'

        got = fedfind.release.get_release('', 'Postrelease', '', 0)
        assert isinstance(got, fedfind.release.PostRelease)
        assert got.compose == datestr
        assert got.release == '23'

    @mock.patch('fedfind.release.RawhideNightly', FakeRelease)
    @mock.patch('fedfind.release.BranchedNightly', FakeRelease)
    @mock.patch('fedfind.release.PostRelease', FakeRelease)
    def test_get_release_guess_respin(self):
        got = fedfind.release.get_release(24, 'Branched', '20160314')
        assert isinstance(got, fedfind.release.BranchedNightly)
        assert got.respin == 3
        got = fedfind.release.get_release('Rawhide', '', '20160314')
        assert isinstance(got, fedfind.release.RawhideNightly)
        assert got.respin == 3
        got = fedfind.release.get_release(23, 'Postrelease', '20160314')
        assert isinstance(got, fedfind.release.PostRelease)
        assert got.respin == 3
