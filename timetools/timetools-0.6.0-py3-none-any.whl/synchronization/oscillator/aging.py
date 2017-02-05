#
# Copyright 2017 Russell Smiley
#
# This file is part of timetools.
#
# timetools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# timetools is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with timetools.  If not, see <http://www.gnu.org/licenses/>.
#


class LinearAging :
    def __init__( self, agingRatePpbPerDay, initialAgePpb = 0, initialAgeTimeSeconds = 0 ) :
        self.__agingRatePpbPerDay = agingRatePpbPerDay
        self.__agingRatePpbPerSecond = self.__agingRatePpbPerDay / (3600 * 24)
        self.__initialAgePpb = initialAgePpb
        self.__initialAgeTimeSeconds = initialAgeTimeSeconds


    def generate( self, referenceTimeSeconds ) :
        offsetTimeSeconds = referenceTimeSeconds - self.__initialAgeTimeSeconds

        ffoPpb = (offsetTimeSeconds * self.__agingRatePpbPerSecond) + self.__initialAgePpb

        return ffoPpb
