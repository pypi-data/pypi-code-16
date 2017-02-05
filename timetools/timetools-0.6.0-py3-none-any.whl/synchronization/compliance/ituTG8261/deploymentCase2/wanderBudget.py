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

import timetools.synchronization.compliance.analysis as tsca


# Rec. ITU-T G.8261/Y.1361 (08/2013), Section 9.1.1.2, Table 3, pp 18

case2A2048MrtieMicroseconds = tsca.Mask([ ([0.05, 0.2], [0, 40]), 
                                     ([0.2, 32], [8]), 
                                     ([32, 64], [0, 0.25]), 
                                     ([64, 1000], [16]) ])
