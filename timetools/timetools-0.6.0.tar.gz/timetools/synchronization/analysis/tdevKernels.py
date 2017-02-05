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

import numpy


def mean (timeError, n, j):
    baseIndex = numpy.arange((j - 1), (n + j - 1))
    
    error1 = timeError[baseIndex + (2 * n)]
    error2 = 2 * timeError[baseIndex + n]
    error3 = timeError[baseIndex]
    
    innerSum = (1 / n) * numpy.sum(error1 - error2 + error3)
    
    return innerSum


def minimum (timeError, n, j):
    baseIndex = numpy.arange((j - 1), (n + j - 1))
    
    error1 = numpy.min(timeError[baseIndex + (2 * n)])
    error2 = 2 * numpy.min(timeError[baseIndex + n])
    error3 = numpy.min(timeError[baseIndex])
    
    innerSum = error1 - error2 + error3
    
    return innerSum
