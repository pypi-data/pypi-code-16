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

from enum import Enum
import numpy


class ToleranceUnit (Enum):
    percent = 1
    absolute = 2
    relative = 3
    
    
class ToleranceException (Exception):
    def __init__ (self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    
    
class ToleranceValue:
    def __init__ (self, expectedValue, toleranceValue, thisToleranceUnit = ToleranceUnit['percent']):
        self.expectedValue = expectedValue
        self.toleranceUnit = thisToleranceUnit
        self.toleranceValue = toleranceValue
        

    def isWithinTolerance (self, array):
        lowerThreshold = None
        upperThreshold = None
        
        thisToleranceUnit = self.toleranceUnit
        if thisToleranceUnit == ToleranceUnit['percent']:
            lowerThreshold, upperThreshold = self._formulatePercentageThresholds(array)
        elif thisToleranceUnit == ToleranceUnit['absolute']:
            lowerThreshold, upperThreshold = self._formulateAbsoluteThresholds(array)
        elif thisToleranceUnit == ToleranceUnit['relative']:
            lowerThreshold, upperThreshold = self._formulateRelativeThresholds(array)
        else:
            raise ToleranceException('Unknown tolerance unit')
        
        return self._calculateThresholdCheck(array, (lowerThreshold, upperThreshold))
    
    
    def _formulatePercentageThresholds (self, array):
        expectedValue = self.expectedValue
        toleranceValue = self.toleranceValue
        
        lowerThreshold = None
        upperThreshold = None
        
        if isinstance(toleranceValue, list):
            # The value is a list
            assert(len(toleranceValue) == 2)
            
            # Assume the first item is the lower threshold and the second item is the upper threshold
            lowerThreshold = expectedValue - (abs(expectedValue) * (toleranceValue[0] / 100))
            upperThreshold = expectedValue + (abs(expectedValue) * (toleranceValue[1] / 100))
        else:
            # Assume toleranceValue is a numeric type
            lowerThreshold = expectedValue - (abs(expectedValue) * (toleranceValue / 100))
            upperThreshold = expectedValue + (abs(expectedValue) * (toleranceValue / 100))
            
        return (lowerThreshold, upperThreshold)
    
    
    def _formulateAbsoluteThresholds (self, array):
        toleranceValue = self.toleranceValue
        
        lowerThreshold = None
        upperThreshold = None
        
        if isinstance(toleranceValue, list):
            # The value is a list
            assert(len(toleranceValue) == 2)
            
            lowerThreshold = toleranceValue[0]
            upperThreshold = toleranceValue[1]
        else:
            raise ToleranceException('Absolute tolerance requires upper and lower thresholds specified')
            
        return (lowerThreshold, upperThreshold)
    
    
    def _formulateRelativeThresholds (self, array):
        expectedValue = self.expectedValue
        toleranceValue = self.toleranceValue
        
        lowerThreshold = None
        upperThreshold = None
        
        if isinstance(toleranceValue, list):
            # The value is a list
            assert(len(toleranceValue) == 2)
            
            lowerThreshold = expectedValue - toleranceValue[0]
            upperThreshold = expectedValue + toleranceValue[1]
        else:
            # Assume toleranceValue is a numeric type
            lowerThreshold = expectedValue - toleranceValue
            upperThreshold = expectedValue + toleranceValue
            
        return (lowerThreshold, upperThreshold)
        
        
    def _calculateThresholdCheck (self, array, toleranceValue):
        return (numpy.all(numpy.logical_and((array <= toleranceValue[1]), (array >= toleranceValue[0]))))
    