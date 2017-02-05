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

import math
import numpy


class referenceGenerator:
    '''
    Generate a uniformly sampled timebase, iteratively as necessary, but of arbitrary size each cycle.
    '''
    
    def __init__ (self, timeStep, initialTimeOffset = 0):
        self._timeStep = timeStep
        # This calculation assumes uniform sampling
        self._lastIterationEndIndex = math.floor(initialTimeOffset / self._timeStep)
    
    
    def generate (self, numberSamples = 1):
        thisIterationIndices = self._lastIterationEndIndex + (numpy.arange(0, numberSamples))
        iterationReferenceTimeSeconds = thisIterationIndices * self._timeStep
        
        self._lastIterationEndIndex = thisIterationIndices[-1] + 1
        
        return iterationReferenceTimeSeconds
    