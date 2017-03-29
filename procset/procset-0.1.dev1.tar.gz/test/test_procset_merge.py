# -*- coding: utf-8 -*-

# Copyright © 2017
# Contributed by Raphaël Bleuse <raphael.bleuse@imag.fr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest
from procset import ProcSet


# The naming convention of the tests follows the one in the position paper by
# the IEEE Interval Standard Working Group - P1788.
# See docs/NehmeierM2010Interval.pdf for further informations.


# pylint: disable=no-self-use,too-many-public-methods
class TestMergeDifference:
    def test_before_ii_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞.........[_]....+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((5, 7))
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_before_ip_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞...........X....+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet(7)
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_before_pi_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞........[__]....+∞
        final: -∞....X...........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((4, 7))
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [0]

    def test_before_pp_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞........X.......+∞
        final: -∞....X...........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(4)
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [0]

    def test_before_ii_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞........[__]....+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((4, 7))
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_before_ip_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞........X.......+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet(4)
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_before_pi_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞.....[_]........+∞
        final: -∞....X...........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((1, 3))
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [0]

    def test_before_pp_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞.....X..........+∞
        final: -∞....X...........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(1)
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [0]

    def test_meets_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞.......[___]....+∞
        final: -∞....[_].........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((3, 7))
        pres = pleft - pright
        assert len(pres) == 3
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2]

    def test_overlaps_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[____]......+∞
        right: -∞......[____]....+∞
        final: -∞....[]..........+∞
        """
        pleft = ProcSet((0, 5))
        pright = ProcSet((2, 7))
        pres = pleft - pright
        assert len(pres) == 2
        assert pres.count() == 1
        assert list(pres) == [0, 1]

    def test_starts_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞....[______]....+∞
        final: -∞................+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((0, 7))
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_starts_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞....[__]........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((0, 3))
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_containedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞......[__]......+∞
        right: -∞....[______]....+∞
        final: -∞................+∞
        """
        pleft = ProcSet((2, 5))
        pright = ProcSet((0, 7))
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_containedby_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....[______]....+∞
        final: -∞................+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet((0, 7))
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_finishes_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞....[______]....+∞
        final: -∞................+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet((0, 7))
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_finishes_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....[__]........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet((0, 3))
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_equal_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞....[__]........+∞
        final: -∞................+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((0, 3))
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_equal_pp(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞....X...........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(0)
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_finishedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞........[__]....+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((4, 7))
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_finishedby_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞...........X....+∞
        final: -∞....[_____].....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(7)
        pres = pleft - pright
        assert len(pres) == 7
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6]

    def test_contains_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞......[__]......+∞
        final: -∞....[]....[]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((2, 5))
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 2
        assert list(pres) == [0, 1, 6, 7]

    def test_contains_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞........X.......+∞
        final: -∞....[__].[_]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(4)
        pres = pleft - pright
        assert len(pres) == 7
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 5, 6, 7]

    def test_startedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞....[__]........+∞
        final: -∞........[__]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((0, 3))
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [4, 5, 6, 7]

    def test_startedby_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞....X...........+∞
        final: -∞.....[_____]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(0)
        pres = pleft - pright
        assert len(pres) == 7
        assert pres.count() == 1
        assert list(pres) == [1, 2, 3, 4, 5, 6, 7]

    def test_overlappedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞.......[___]....+∞
        right: -∞....[____]......+∞
        final: -∞..........[]....+∞
        """
        pleft = ProcSet((3, 7))
        pright = ProcSet((0, 5))
        pres = pleft - pright
        assert len(pres) == 2
        assert pres.count() == 1
        assert list(pres) == [6, 7]

    def test_metby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[___].......+∞
        right: -∞........[__]....+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 4))
        pright = ProcSet((4, 7))
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_after_ii_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞..........[]....+∞
        right: -∞......[]........+∞
        final: -∞..........[]....+∞
        """
        pleft = ProcSet((6, 7))
        pright = ProcSet((2, 3))
        pres = pleft - pright
        assert len(pres) == 2
        assert pres.count() == 1
        assert list(pres) == [6, 7]

    def test_after_pi_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞.........X......+∞
        right: -∞....[__]........+∞
        final: -∞.........X......+∞
        """
        pleft = ProcSet(5)
        pright = ProcSet((0, 3))
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [5]

    def test_after_ip_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞....X...........+∞
        final: -∞........[__]....+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet(0)
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [4, 5, 6, 7]

    def test_after_pp_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....X...........+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet(0)
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_after_ii_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞..........[]....+∞
        right: -∞......[__]......+∞
        final: -∞..........[]....+∞
        """
        pleft = ProcSet((6, 7))
        pright = ProcSet((2, 5))
        pres = pleft - pright
        assert len(pres) == 2
        assert pres.count() == 1
        assert list(pres) == [6, 7]

    def test_after_pi_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞.........X......+∞
        right: -∞....[___].......+∞
        final: -∞.........X......+∞
        """
        pleft = ProcSet(5)
        pright = ProcSet((0, 4))
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [5]

    def test_after_ip_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞.......X........+∞
        final: -∞........[__]....+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet(3)
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [4, 5, 6, 7]

    def test_after_pp_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞......X.........+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet(2)
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_firstempty_i(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞......[__]......+∞
        final: -∞................+∞
        """
        pleft = ProcSet()
        pright = ProcSet((2, 5))
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_firstempy_p(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞.......X........+∞
        final: -∞................+∞
        """
        pleft = ProcSet()
        pright = ProcSet(3)
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_secondempty_i(self):
        """
               -∞....01234567....+∞
        left:  -∞......[__]......+∞
        right: -∞................+∞
        final: -∞......[__]......+∞
        """
        pleft = ProcSet((2, 5))
        pright = ProcSet()
        pres = pleft - pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5]

    def test_secondempty_p(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞................+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet()
        pres = pleft - pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_bothempty(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞................+∞
        final: -∞................+∞
        """
        pleft = ProcSet()
        pright = ProcSet()
        pres = pleft - pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []


# pylint: disable=no-self-use,too-many-public-methods
class TestMergeIntersection:
    def test_before_ii_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞.........[_]....+∞
        final: -∞................+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((5, 7))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_before_ip_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞...........X....+∞
        final: -∞................+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet(7)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_before_pi_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞........[__]....+∞
        final: -∞................+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((4, 7))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_before_pp_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞........X.......+∞
        final: -∞................+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(4)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_before_ii_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞........[__]....+∞
        final: -∞................+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((4, 7))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_before_ip_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞........X.......+∞
        final: -∞................+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet(4)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_before_pi_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞.....[_]........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((1, 3))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_before_pp_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞.....X..........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(1)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_meets_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞.......[___]....+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((3, 7))
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_overlaps_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[____]......+∞
        right: -∞......[____]....+∞
        final: -∞......[__]......+∞
        """
        pleft = ProcSet((0, 5))
        pright = ProcSet((2, 7))
        pres = pleft & pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5]

    def test_starts_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞....[______]....+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((0, 7))
        pres = pleft & pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_starts_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞....[__]........+∞
        final: -∞....X...........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((0, 3))
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [0]

    def test_containedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞......[__]......+∞
        right: -∞....[______]....+∞
        final: -∞......[__]......+∞
        """
        pleft = ProcSet((2, 5))
        pright = ProcSet((0, 7))
        pres = pleft & pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5]

    def test_containedby_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....[______]....+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet((0, 7))
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_finishes_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞....[______]....+∞
        final: -∞........[__]....+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet((0, 7))
        pres = pleft & pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [4, 5, 6, 7]

    def test_finishes_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....[__]........+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet((0, 3))
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_equal_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞....[__]........+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((0, 3))
        pres = pleft & pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_equal_pp(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞....X...........+∞
        final: -∞....X...........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(0)
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [0]

    def test_finishedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞........[__]....+∞
        final: -∞........[__]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((4, 7))
        pres = pleft & pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [4, 5, 6, 7]

    def test_finishedby_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞...........X....+∞
        final: -∞...........X....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(7)
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [7]

    def test_contains_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞......[__]......+∞
        final: -∞......[__]......+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((2, 5))
        pres = pleft & pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5]

    def test_contains_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞........X.......+∞
        final: -∞........X.......+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(4)
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [4]

    def test_startedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞....[__]........+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((0, 3))
        pres = pleft & pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_startedby_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞....X...........+∞
        final: -∞....X...........+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(0)
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [0]

    def test_overlappedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞.......[___]....+∞
        right: -∞....[____]......+∞
        final: -∞.......[_]......+∞
        """
        pleft = ProcSet((3, 7))
        pright = ProcSet((0, 5))
        pres = pleft & pright
        assert len(pres) == 3
        assert pres.count() == 1
        assert list(pres) == [3, 4, 5]

    def test_metby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[___].......+∞
        right: -∞........[__]....+∞
        final: -∞........X.......+∞
        """
        pleft = ProcSet((0, 4))
        pright = ProcSet((4, 7))
        pres = pleft & pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [4]

    def test_after_ii_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞..........[]....+∞
        right: -∞......[]........+∞
        final: -∞................+∞
        """
        pleft = ProcSet((6, 7))
        pright = ProcSet((2, 3))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_after_pi_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞.........X......+∞
        right: -∞....[__]........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(5)
        pright = ProcSet((0, 3))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_after_ip_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞....X...........+∞
        final: -∞................+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet(0)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_after_pp_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....X...........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet(0)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_after_ii_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞..........[]....+∞
        right: -∞......[__]......+∞
        final: -∞................+∞
        """
        pleft = ProcSet((6, 7))
        pright = ProcSet((2, 5))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_after_pi_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞.........X......+∞
        right: -∞....[___].......+∞
        final: -∞................+∞
        """
        pleft = ProcSet(5)
        pright = ProcSet((0, 4))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_after_ip_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞.......X........+∞
        final: -∞................+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet(3)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_after_pp_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞......X.........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet(2)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_firstempty_i(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞......[__]......+∞
        final: -∞................+∞
        """
        pleft = ProcSet()
        pright = ProcSet((2, 5))
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_firstempy_p(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞.......X........+∞
        final: -∞................+∞
        """
        pleft = ProcSet()
        pright = ProcSet(3)
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_secondempty_i(self):
        """
               -∞....01234567....+∞
        left:  -∞......[__]......+∞
        right: -∞................+∞
        final: -∞................+∞
        """
        pleft = ProcSet((2, 5))
        pright = ProcSet()
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_secondempty_p(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞................+∞
        final: -∞................+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet()
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_bothempty(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞................+∞
        final: -∞................+∞
        """
        pleft = ProcSet()
        pright = ProcSet()
        pres = pleft & pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []


# pylint: disable=no-self-use,too-many-public-methods
class TestMergeSymmetricDifference:
    def test_before_ii_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞.........[_]....+∞
        final: -∞....[__] [_]....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((5, 7))
        pres = pleft ^ pright
        assert len(pres) == 7
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 5, 6, 7]

    def test_before_ip_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞...........X....+∞
        final: -∞....[__]...X....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet(7)
        pres = pleft ^ pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 7]

    def test_before_pi_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞........[__]....+∞
        final: -∞....X...[__]....+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((4, 7))
        pres = pleft ^ pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 4, 5, 6, 7]

    def test_before_pp_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞........X.......+∞
        final: -∞....X...X.......+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(4)
        pres = pleft ^ pright
        assert len(pres) == 2
        assert pres.count() == 2
        assert list(pres) == [0, 4]

    def test_before_ii_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞........[__]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((4, 7))
        pres = pleft ^ pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_before_ip_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞........X.......+∞
        final: -∞....[___].......+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet(4)
        pres = pleft ^ pright
        assert len(pres) == 5
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4]

    def test_before_pi_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞.....[_]........+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((1, 3))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_before_pp_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞.....X..........+∞
        final: -∞....[]..........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(1)
        pres = pleft ^ pright
        assert len(pres) == 2
        assert pres.count() == 1
        assert list(pres) == [0, 1]

    def test_meets_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞.......[___]....+∞
        final: -∞....[_].[__]....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((3, 7))
        pres = pleft ^ pright
        assert len(pres) == 7
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 4, 5, 6, 7]

    def test_overlaps_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[____]......+∞
        right: -∞......[____]....+∞
        final: -∞....[]....[]....+∞
        """
        pleft = ProcSet((0, 5))
        pright = ProcSet((2, 7))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 2
        assert list(pres) == [0, 1, 6, 7]

    def test_starts_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞....[______]....+∞
        final: -∞........[__]....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((0, 7))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [4, 5, 6, 7]

    def test_starts_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞....[__]........+∞
        final: -∞.....[_]........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((0, 3))
        pres = pleft ^ pright
        assert len(pres) == 3
        assert pres.count() == 1
        assert list(pres) == [1, 2, 3]

    def test_containedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞......[__]......+∞
        right: -∞....[______]....+∞
        final: -∞....[]....[]....+∞
        """
        pleft = ProcSet((2, 5))
        pright = ProcSet((0, 7))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 2
        assert list(pres) == [0, 1, 6, 7]

    def test_containedby_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....[______]....+∞
        final: -∞....[_].[__]....+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet((0, 7))
        pres = pleft ^ pright
        assert len(pres) == 7
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 4, 5, 6, 7]

    def test_finishes_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞....[______]....+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet((0, 7))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_finishes_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....[__]........+∞
        final: -∞....[_].........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet((0, 3))
        pres = pleft ^ pright
        assert len(pres) == 3
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2]

    def test_equal_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞....[__]........+∞
        final: -∞................+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((0, 3))
        pres = pleft ^ pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_equal_pp(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞....X...........+∞
        final: -∞................+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(0)
        pres = pleft ^ pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []

    def test_finishedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞........[__]....+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((4, 7))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_finishedby_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞...........X....+∞
        final: -∞....[_____].....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(7)
        pres = pleft ^ pright
        assert len(pres) == 7
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6]

    def test_contains_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞......[__]......+∞
        final: -∞....[]....[]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((2, 5))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 2
        assert list(pres) == [0, 1, 6, 7]

    def test_contains_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞........X.......+∞
        final: -∞....[__].[_]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(4)
        pres = pleft ^ pright
        assert len(pres) == 7
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 5, 6, 7]

    def test_startedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞....[__]........+∞
        final: -∞........[__]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((0, 3))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [4, 5, 6, 7]

    def test_startedby_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞....X...........+∞
        final: -∞.....[_____]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(0)
        pres = pleft ^ pright
        assert len(pres) == 7
        assert pres.count() == 1
        assert list(pres) == [1, 2, 3, 4, 5, 6, 7]

    def test_overlappedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞.......[___]....+∞
        right: -∞....[____]......+∞
        final: -∞....[_]...[]....+∞
        """
        pleft = ProcSet((3, 7))
        pright = ProcSet((0, 5))
        pres = pleft ^ pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 6, 7]

    def test_metby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[___].......+∞
        right: -∞........[__]....+∞
        final: -∞....[__].[_]....+∞
        """
        pleft = ProcSet((0, 4))
        pright = ProcSet((4, 7))
        pres = pleft ^ pright
        assert len(pres) == 7
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 5, 6, 7]

    def test_after_ii_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞..........[]....+∞
        right: -∞......[]........+∞
        final: -∞......[]..[]....+∞
        """
        pleft = ProcSet((6, 7))
        pright = ProcSet((2, 3))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 2
        assert list(pres) == [2, 3, 6, 7]

    def test_after_pi_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞.........X......+∞
        right: -∞....[__]........+∞
        final: -∞....[__].X......+∞
        """
        pleft = ProcSet(5)
        pright = ProcSet((0, 3))
        pres = pleft ^ pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 5]

    def test_after_ip_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞....X...........+∞
        final: -∞....X...[__]....+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet(0)
        pres = pleft ^ pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 4, 5, 6, 7]

    def test_after_pp_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....X...........+∞
        final: -∞....X..X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet(0)
        pres = pleft ^ pright
        assert len(pres) == 2
        assert pres.count() == 2
        assert list(pres) == [0, 3]

    def test_after_ii_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞..........[]....+∞
        right: -∞......[__]......+∞
        final: -∞......[____]....+∞
        """
        pleft = ProcSet((6, 7))
        pright = ProcSet((2, 5))
        pres = pleft ^ pright
        assert len(pres) == 6
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5, 6, 7]

    def test_after_pi_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞.........X......+∞
        right: -∞....[___].......+∞
        final: -∞....[____]......+∞
        """
        pleft = ProcSet(5)
        pright = ProcSet((0, 4))
        pres = pleft ^ pright
        assert len(pres) == 6
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5]

    def test_after_ip_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞.......X........+∞
        final: -∞.......[___]....+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet(3)
        pres = pleft ^ pright
        assert len(pres) == 5
        assert pres.count() == 1
        assert list(pres) == [3, 4, 5, 6, 7]

    def test_after_pp_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞......X.........+∞
        final: -∞......[]........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet(2)
        pres = pleft ^ pright
        assert len(pres) == 2
        assert pres.count() == 1
        assert list(pres) == [2, 3]

    def test_firstempty_i(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞......[__]......+∞
        final: -∞......[__]......+∞
        """
        pleft = ProcSet()
        pright = ProcSet((2, 5))
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5]

    def test_firstempy_p(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞.......X........+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet()
        pright = ProcSet(3)
        pres = pleft ^ pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_secondempty_i(self):
        """
               -∞....01234567....+∞
        left:  -∞......[__]......+∞
        right: -∞................+∞
        final: -∞......[__]......+∞
        """
        pleft = ProcSet((2, 5))
        pright = ProcSet()
        pres = pleft ^ pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5]

    def test_secondempty_p(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞................+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet()
        pres = pleft ^ pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_bothempty(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞................+∞
        final: -∞................+∞
        """
        pleft = ProcSet()
        pright = ProcSet()
        pres = pleft ^ pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []


# pylint: disable=no-self-use,too-many-public-methods
class TestMergeUnion:
    def test_before_ii_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞.........[_]....+∞
        final: -∞....[__].[_]....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((5, 7))
        pres = pleft | pright
        assert len(pres) == 7
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 5, 6, 7]

    def test_before_ip_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞...........X....+∞
        final: -∞....[__]...X....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet(7)
        pres = pleft | pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 7]

    def test_before_pi_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞........[__]....+∞
        final: -∞....X...[__]....+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((4, 7))
        pres = pleft | pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 4, 5, 6, 7]

    def test_before_pp_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞........X.......+∞
        final: -∞....X...X.......+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(4)
        pres = pleft | pright
        assert len(pres) == 2
        assert pres.count() == 2
        assert list(pres) == [0, 4]

    def test_before_ii_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞........[__]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((4, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_before_ip_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞........X.......+∞
        final: -∞....[___].......+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet(4)
        pres = pleft | pright
        assert len(pres) == 5
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4]

    def test_before_pi_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞.....[_]........+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((1, 3))
        pres = pleft | pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_before_pp_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞.....X..........+∞
        final: -∞....[]..........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(1)
        pres = pleft | pright
        assert len(pres) == 2
        assert pres.count() == 1
        assert list(pres) == [0, 1]

    def test_meets_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞.......[___]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((3, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_overlaps_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[____]......+∞
        right: -∞......[____]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 5))
        pright = ProcSet((2, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_starts_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞....[______]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((0, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_starts_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞....[__]........+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet((0, 3))
        pres = pleft | pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_containedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞......[__]......+∞
        right: -∞....[______]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((2, 5))
        pright = ProcSet((0, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_containedby_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....[______]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet((0, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_finishes_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞....[______]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet((0, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_finishes_pi(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....[__]........+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet((0, 3))
        pres = pleft | pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_equal_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[__]........+∞
        right: -∞....[__]........+∞
        final: -∞....[__]........+∞
        """
        pleft = ProcSet((0, 3))
        pright = ProcSet((0, 3))
        pres = pleft | pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3]

    def test_equal_pp(self):
        """
               -∞....01234567....+∞
        left:  -∞....X...........+∞
        right: -∞....X...........+∞
        final: -∞....X...........+∞
        """
        pleft = ProcSet(0)
        pright = ProcSet(0)
        pres = pleft | pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [0]

    def test_finishedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞........[__]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((4, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_finishedby_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞...........X....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(7)
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_contains_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞......[__]......+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((2, 5))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_contains_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞........X.......+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(4)
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_startedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞....[__]........+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet((0, 3))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_startedby_ip(self):
        """
               -∞....01234567....+∞
        left:  -∞....[______]....+∞
        right: -∞....X...........+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 7))
        pright = ProcSet(0)
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_overlappedby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞.......[___]....+∞
        right: -∞....[____]......+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((3, 7))
        pright = ProcSet((0, 5))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_metby_ii(self):
        """
               -∞....01234567....+∞
        left:  -∞....[___].......+∞
        right: -∞........[__]....+∞
        final: -∞....[______]....+∞
        """
        pleft = ProcSet((0, 4))
        pright = ProcSet((4, 7))
        pres = pleft | pright
        assert len(pres) == 8
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5, 6, 7]

    def test_after_ii_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞..........[]....+∞
        right: -∞......[]........+∞
        final: -∞......[]..[]....+∞
        """
        pleft = ProcSet((6, 7))
        pright = ProcSet((2, 3))
        pres = pleft | pright
        assert len(pres) == 4
        assert pres.count() == 2
        assert list(pres) == [2, 3, 6, 7]

    def test_after_pi_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞.........X......+∞
        right: -∞....[__]........+∞
        final: -∞....[__].X......+∞
        """
        pleft = ProcSet(5)
        pright = ProcSet((0, 3))
        pres = pleft | pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 1, 2, 3, 5]

    def test_after_ip_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞....X...........+∞
        final: -∞....X...[__]....+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet(0)
        pres = pleft | pright
        assert len(pres) == 5
        assert pres.count() == 2
        assert list(pres) == [0, 4, 5, 6, 7]

    def test_after_pp_notouch(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞....X...........+∞
        final: -∞....X..X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet(0)
        pres = pleft | pright
        assert len(pres) == 2
        assert pres.count() == 2
        assert list(pres) == [0, 3]

    def test_after_ii_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞..........[]....+∞
        right: -∞......[__]......+∞
        final: -∞......[____]....+∞
        """
        pleft = ProcSet((6, 7))
        pright = ProcSet((2, 5))
        pres = pleft | pright
        assert len(pres) == 6
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5, 6, 7]

    def test_after_pi_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞.........X......+∞
        right: -∞....[___].......+∞
        final: -∞....[____]......+∞
        """
        pleft = ProcSet(5)
        pright = ProcSet((0, 4))
        pres = pleft | pright
        assert len(pres) == 6
        assert pres.count() == 1
        assert list(pres) == [0, 1, 2, 3, 4, 5]

    def test_after_ip_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞........[__]....+∞
        right: -∞.......X........+∞
        final: -∞.......[___]....+∞
        """
        pleft = ProcSet((4, 7))
        pright = ProcSet(3)
        pres = pleft | pright
        assert len(pres) == 5
        assert pres.count() == 1
        assert list(pres) == [3, 4, 5, 6, 7]

    def test_after_pp_touch(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞......X.........+∞
        final: -∞......[]........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet(2)
        pres = pleft | pright
        assert len(pres) == 2
        assert pres.count() == 1
        assert list(pres) == [2, 3]

    def test_firstempty_i(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞......[__]......+∞
        final: -∞......[__]......+∞
        """
        pleft = ProcSet()
        pright = ProcSet((2, 5))
        pres = pleft | pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5]

    def test_firstempy_p(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞.......X........+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet()
        pright = ProcSet(3)
        pres = pleft | pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_secondempty_i(self):
        """
               -∞....01234567....+∞
        left:  -∞......[__]......+∞
        right: -∞................+∞
        final: -∞......[__]......+∞
        """
        pleft = ProcSet((2, 5))
        pright = ProcSet()
        pres = pleft | pright
        assert len(pres) == 4
        assert pres.count() == 1
        assert list(pres) == [2, 3, 4, 5]

    def test_secondempty_p(self):
        """
               -∞....01234567....+∞
        left:  -∞.......X........+∞
        right: -∞................+∞
        final: -∞.......X........+∞
        """
        pleft = ProcSet(3)
        pright = ProcSet()
        pres = pleft | pright
        assert len(pres) == 1
        assert pres.count() == 1
        assert list(pres) == [3]

    def test_bothempty(self):
        """
               -∞....01234567....+∞
        left:  -∞................+∞
        right: -∞................+∞
        final: -∞................+∞
        """
        pleft = ProcSet()
        pright = ProcSet()
        pres = pleft | pright
        assert len(pres) == 0
        assert pres.count() == 0
        assert list(pres) == []
