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

import numpy.random as nr
    
    
class GaussianParameters:
    
    def __init__ (self, mean = 0, standardDeviation = 1, lowerThreshold = None, upperThreshold = None, randomSeed = None):
        self.mean = mean
        self.standardDeviation = standardDeviation
        self.upperThreshold = upperThreshold
        self.lowerThreshold = lowerThreshold
        
        self.randomGenerator = None
        if randomSeed is not None:
            # Assume randomSeed is a 32 bit integer
            self.randomGenerator = nr.RandomState(randomSeed)
        else:
            self.randomGenerator = nr.RandomState()
    
    
class UniformParameters:
    
    def __init__ (self, lowerThreshold = 0, upperThreshold = 1, randomSeed = None):
        self.upperThreshold = upperThreshold
        self.lowerThreshold = lowerThreshold
        
        self.randomGenerator = None
        if randomSeed is not None:
            # Assume randomSeed is a 32 bit integer
            self.randomGenerator = nr.RandomState(randomSeed)
        else:
            self.randomGenerator = nr.RandomState()
    
    
class ExponentialParameters:
    
    def __init__ (self, offset = 0, scale = 1, upperThreshold = None, randomSeed = None):
        self.offset = offset
        self.scale = scale
        self.upperThreshold = upperThreshold
        
        self.randomGenerator = None
        if randomSeed is not None:
            # Assume randomSeed is a 32 bit integer
            self.randomGenerator = nr.RandomState(randomSeed)
        else:
            self.randomGenerator = nr.RandomState()
        