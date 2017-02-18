# -*- coding: utf-8  -*-
"""Base classes for matches."""

# Copyright (C) 2015-17 Alexander Jones
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals


class Match(object):

    """Base class for matches."""

    def play(self):
        """Play the match."""
        raise NotImplementedError


class TwoCompetitorMatch(Match):

    """Base class for matches with exactly two competitors."""

    @property
    def competitor1(self):
        """The first (usually home) competitor."""
        raise NotImplementedError

    @property
    def competitor2(self):
        """The second (usually away) competitor."""
        raise NotImplementedError

    @property
    def is_walkover(self):
        """Whether or not this match is a walkover/bye."""
        return self.competitor1 is None or self.competitor2 is None


class TwoTeamMatch(TwoCompetitorMatch):

    """Base class for two-team matches."""

    def __init__(self, team1, team2):
        """Constructor.

        @param team1: The first (home) team
        @type team1: An object that can be converted to a string
        @param team2: The second (away) team
        @type team2: An object that can be converted to a string
        """
        self.team1 = team1
        self.team2 = team2

    @property
    def competitor1(self):
        """The first (usually home) competitor."""
        return self.team1

    @property
    def competitor2(self):
        """The second (usually away) competitor."""
        return self.team2


class TwoPlayerMatch(TwoCompetitorMatch):

    """Base class for two-player matches."""

    def __init__(self, player1, player2):
        """Constructor.

        @param player1: The first (home) player
        @type player1: An object that can be converted to a string
        @param player2: The second (away) player
        @type player2: An object that can be converted to a string
        """
        self.player1 = player1
        self.player2 = player2

    @property
    def competitor1(self):
        """The first (usually home) competitor."""
        return self.player1

    @property
    def competitor2(self):
        """The second (usually away) competitor."""
        return self.player2
