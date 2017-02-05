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


class Predefined:
    
    def __init__ (self, pdvData):
        self._pdvData = pdvData
        self._lastIterationOffset = 0
        
        
    def generate (self, timebaseSeconds):
        # PDV data is applied like a ring buffer against iterations of time bases.
        offsetIndices = numpy.arange(0, len(timebaseSeconds)) + self._lastIterationOffset
        ringIndices = numpy.mod(offsetIndices, len(self._pdvData))
        
        self._lastIterationOffset += len(timebaseSeconds)
        
        return self._pdvData[ringIndices]
    

class Gaussian:
    
    def __init__ (self, parameters):
        self._mean = parameters.mean
        self._standardDeviation = parameters.standardDeviation
        self._lowerThreshold = parameters.lowerThreshold
        self._upperThreshold = parameters.upperThreshold
        self._randomGenerator = parameters.randomGenerator
        
        
    def generate (self, timebaseSeconds):
        numberSamples = len(timebaseSeconds)
        
        thisPdv = self._randomGenerator.normal(self._mean, self._standardDeviation, numberSamples)
        
        if self._upperThreshold != None:
            thisPdv[thisPdv > self._upperThreshold] = self._upperThreshold
            
        if self._lowerThreshold != None:
            thisPdv[thisPdv < self._lowerThreshold] = self._lowerThreshold
        
        return thisPdv


class Uniform:
    
    def __init__ (self, parameters):
        self._lowerThreshold = parameters.lowerThreshold
        self._upperThreshold = parameters.upperThreshold
        self._randomGenerator = parameters.randomGenerator


    def generate (self, timebaseSeconds):
        numberSamples = len(timebaseSeconds)
        
        thisPdv = self._randomGenerator.uniform(self._lowerThreshold, self._upperThreshold, numberSamples)
        
        return thisPdv
    

class Exponential:
    
    def __init__ (self, parameters):
        self._offset = parameters.offset
        self._scale = parameters.scale
        self._upperThreshold = parameters.upperThreshold
        self._randomGenerator = parameters.randomGenerator
    
    
    def generate (self, timebaseSeconds):
        numberSamples = len(timebaseSeconds)
        
        thisPdv = self._randomGenerator.exponential(self._scale, numberSamples) + self._offset
        
        if self._upperThreshold != None:
            thisPdv[thisPdv > self._upperThreshold] = self._upperThreshold
        
        return thisPdv

