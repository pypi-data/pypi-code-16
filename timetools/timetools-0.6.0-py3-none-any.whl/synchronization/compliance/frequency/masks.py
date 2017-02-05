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

import timetools.synchronization.compliance.general as generalCompliance


ffo16ppbMask = generalCompliance.createSimpleThresholdMask(16, 0, lowerThreshold=-16)


def generateThresholdMask (ffoThresholdPpb):
    ffoPpbMask = generalCompliance.createSimpleThresholdMask(ffoThresholdPpb, 0, lowerThreshold=-ffoThresholdPpb)
    
    return ffoPpbMask
