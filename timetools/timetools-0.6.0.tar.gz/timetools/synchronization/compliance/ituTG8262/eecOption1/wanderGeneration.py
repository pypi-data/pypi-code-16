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


# ITU-T G.8262/Y.1362 (07/2010), pp 4-5

# Table 1
mtieConstantTemperatureNs = tsca.Mask([ ([0.1, 1], [40]), 
                                       ([1, 100], ([40], [0.1]) ), 
                                       ([100, 1000], ([25.25], [0.2])) ])

# Table 2
mtieTemperatureNs = tsca.Mask([ ([0.1, 1], ([40, 0.5], [0, 1]) ), 
                               ([1, 100], ([40, 0.5], [0.1, 1]) ), 
                               ([100, 1000], ([50, 25.25], [0, 0.2])) ])

# Table 3
tdevConstantTemperatureNs = tsca.Mask([ ([0.1, 25], [3.2]),
                                       ([25, 100], ([0.64], [0.5])), 
                                       ([100, 1000], [6.4]) ])
