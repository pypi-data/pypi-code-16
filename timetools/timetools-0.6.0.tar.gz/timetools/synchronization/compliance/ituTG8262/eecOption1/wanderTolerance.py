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

import timetools.synchronization.compliance.analysis as tsca


# ITU-T G.8262/Y.1362 (07/2010), pp 9-10

# Table 7
mtieMicroseconds = tsca.Mask([ ([0.1, 2.5], [0.25]), 
                              ([2.5, 20], [0, 0.1]), 
                              ([20, 400], [2]), 
                              ([400, 1000], [0, 0.005])])

# Table 8
tdevNs = tsca.Mask([ ([0.1, 7], [12]), 
                    ([7, 100], [0, 1.7]), 
                    ([100, 1000], [170])])


def generateSinusoidalMask ():
    '''
    ITU-T G.8262/Y.1362 (07/2010), Table 9, pp 10
    '''
    def solveSegment (frequency, amplitude):
        result = numpy.linalg.solve(numpy.array([[numpy.log10(frequency[0]), 1], [numpy.log10(frequency[1]), 1]]), numpy.log10(amplitude))
        # Assume the frequency are listed in increasing order
        interval = (frequency.tolist(), ([numpy.power(10, result[1])], [result[0]]) )
        return interval
    
    
    wanderAmplitudeMicroseconds = numpy.array([0.25, 2, 5])
    frequenciesHz = numpy.array([0.32e-3, 0.8e-3, 16e-3, 0.13, 10])
    
    outputMask = tsca.Mask([])
    
    firstInterval = solveSegment(frequenciesHz[0:2], wanderAmplitudeMicroseconds[2:0:-1])
    outputMask.addInterval(firstInterval)
    
    outputMask.addInterval( (frequenciesHz[1:3].tolist(), [wanderAmplitudeMicroseconds[1]]) )
    
    thirdInterval = solveSegment(frequenciesHz[2:4], wanderAmplitudeMicroseconds[1::-1])
    outputMask.addInterval(thirdInterval)
    
    outputMask.addInterval( (frequenciesHz[3:5].tolist(), [wanderAmplitudeMicroseconds[0]]) )
    
    return outputMask
