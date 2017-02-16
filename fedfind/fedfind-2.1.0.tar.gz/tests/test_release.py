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

import fedfind.release

# config decorators
net = pytest.mark.net

class TestRelease:
    """Tests for release.py."""

    def test_get_release_offline(self):
        """Offline tests for get_release."""
        datestr = datetime.date.today().strftime('%Y%m%d')
        rels = (
            # Archive stable.
            ((15, '', ''), (fedfind.release.ArchiveRelease, '15')),
            # Fedora Core stable (release string).
            (('6', '', ''), (fedfind.release.CoreRelease, '6')),
            # 'Final' treated as stable.
            (('6', 'Final', ''), (fedfind.release.CoreRelease, '6')),
            # Milestone. FIXME: disabled till we know how these will be with Pungi 4.
            #((23, 'Beta', ''), (fedfind.release.Milestone, '23', 'Beta')),
            # TC/RC. FIXME: disabled till we know how these will be with Pungi 4.
            #((23, 'Beta', 'RC1'), (fedfind.release.Compose, '23', 'Beta', 'RC1')),
            # Post-release stable nightly (date string).
            ((22, 'Postrelease', datestr), (fedfind.release.PostRelease, '22', 'Postrelease', datestr)),
            # Branched nightly.
            ((23, 'Branched', datestr), (fedfind.release.BranchedNightly, '23', 'Branched', datestr)),
            # Rawhide nightly.
            (('Rawhide', '', datestr), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr)),
            # Wikitcms format Rawhide.
            (('24', 'Rawhide', datestr), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr)),
            # OFFLINE GUESSES
            # Date guesses.
            ((23, 'Branched', ''), (fedfind.release.BranchedNightly, '23', 'Branched', datestr)),
            (('Rawhide', '', ''), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr)),
            ((22, 'Postrelease', ''), (fedfind.release.PostRelease, '22', 'Postrelease', datestr)),
            # Default, check None is handled.
            ((None, None, None), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr)),
        )

        # Test that various get_release() invocations return expected
        # classes and values. Each rel's first tuple is the release,
        # milestone, compose values to pass to get_release. Its second
        # tuple's first value is always the expected class. The next
        # three values of the second tuple are optional, and they are
        # the expected release, milestone and compose; each will be
        # checked if present.
        for ((release, milestone, compose), expected) in rels:
            got = fedfind.release.get_release(release, milestone, compose, 0)
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

        # Sanity check tests.
        with pytest.raises(ValueError):
            fedfind.release.get_release('foobar')

        with pytest.raises(ValueError):
            fedfind.release.get_release('23', '', 'RC2')

    @net
    def test_get_release_online(self):
        """Online tests for get_release."""
        # Current-ish stable.
        # NOTE: this test will need periodic updating.
        got = fedfind.release.get_release('23')
        assert isinstance(got, fedfind.release.CurrentRelease)


        # Release guessing. We can't test this very hard or we'd have
        # to keep updating the tests all the goddamned time, or the
        # test would duplicate the logic of get_current_release and
        # that seems pointless. But we can at least check it's not
        # crashing and returns the right class.
        datestr = datetime.date.today().strftime('%Y%m%d')

        got = fedfind.release.get_release('', 'Branched', '')
        assert isinstance(got, fedfind.release.BranchedNightly)
        assert got.compose == datestr

        got = fedfind.release.get_release('', 'Postrelease', '')
        assert isinstance(got, fedfind.release.PostRelease)
        assert got.compose == datestr
