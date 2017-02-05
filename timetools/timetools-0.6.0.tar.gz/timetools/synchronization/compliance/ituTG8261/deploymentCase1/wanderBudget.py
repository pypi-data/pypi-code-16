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


# Rec. ITU-T G.8261/Y.1361 (08/2013), Section 9.1.1.1, Table 2, pp 17

case11544MrtieMicroseconds = tsca.Mask([ ([0.1, 0.47], [0, 4.5]), 
                                        ([0.47, 900], [2.1]), 
                                        ([900, 1930], [0, 2.33e-3]), 
                                        ([1930, 86400], [4.5]) ])


# Rec. ITU-T G.8261/Y.1361 (08/2013), Section 9.1.1.1, Table 1, pp 16

case12048MrtieMicroseconds = tsca.Mask([ ([0.05, 0.2], [0, 10.75]), 
                                        ([0.2, 32], [9 * 0.24]), 
                                        ([32, 64], [0, 0.067]), 
                                        ([64, 1000], [18 * 0.24]) ])
