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


# Rec. ITU-T G.8261/Y.1361 (08/2013), Section 9.2.1.1, Table 4, pp 20

mtieNs = tsca.Mask([ ([0.1, 2.5], [250]), 
                    ([2.5, 20], [0, 100]), 
                    ([20, 2000], [2000]), 
                    ([2000], ([0.01, 433], [1, 0.2])) ])


# Rec. ITU-T G.8261/Y.1361 (08/2013), Section 9.2.1.1, Table 5, pp 21

tdevNs = tsca.Mask([ ([0.1, 17.14], [12]), 
                    ([17.14, 100], [0, 0.7]), 
                    ([100, 1e6], ([58, 1.2, 3e-4], [0, 0.5, 1])) ])
