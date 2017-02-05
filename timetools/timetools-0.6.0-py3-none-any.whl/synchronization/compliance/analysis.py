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
import numpy.polynomial.polynomial as polynomial
import matplotlib.pyplot as mpp


class ComplianceException (Exception):
    
    def __init__ (self, value):
        self.value = value
        
        
    def __str__(self):
        return repr(self.value)


class ValidationException (Exception):
    
    def __init__ (self, value):
        self.value = value
        
        
    def __str__(self):
        return repr(self.value)


class Mask:
    '''
    A mask is comprised of a set of intervals over which a signal may be 
    analysed for compliance to the mask specification.
    '''
    def __init__ (self, intervalSet):
        self._intervalSet = intervalSet
        
        self._validateIntervalSet()
        
        
    def evaluate (self, signal):
        '''
        Establish that the signal is always within the specified mask bounds.
        '''
        result = True
        for thisInterval in self._intervalSet:
            if len(thisInterval) == 2:
                # Upper bound only spec
                result = self._evaluateUpperBound(thisInterval, signal)
                
            elif len(thisInterval) == 3:
                # lower & upper bound spec
                result = self._evaluateUpperLowerBound(thisInterval, signal)
                    
            else:
                raise ValidationException('Wrong number of elements in interval tuple')
                
        return result
    
    
    def addToPlot (self, figureInstanceNumber, *args, **kwargs):
        '''
        Add the mask to the specified Matplotlib figure.
        '''
        mpp.figure(figureInstanceNumber)
        
        for thisInterval in self._intervalSet:
            if len(thisInterval) == 2:
                # Upper bound only spec
                self._plotIntervalUpperBound(thisInterval, kwargs)
                
            elif len(thisInterval) == 3:
                # lower & upper bound spec
                self._plotIntervalUpperLowerBound(thisInterval, kwargs)
                
            else:
                raise ValidationException('Wrong number of elements in interval tuple')
               
    
    def addInterval (self, interval):
        '''
        Add an interval to the mask specification.
        '''
        self._intervalSet.append(interval)
        
        self._validateIntervalSet()
        
    
    def _validateIntervalSet(self):
        # An intervalSet is a list of tuples
        # Intervals cannot overlap
        
        # Python is usually duck typed (if it walks like a duck and quacks like a duck...).
        # In this case we are using the sequence of lists and tuples to encode the type of
        # interval information being used so strict typing is applied instead.
        assert(isinstance(self._intervalSet, list))
        for interval in self._intervalSet:
            # An interval is a tuple of size 2 or 3
            #   * A size 2 tuple implies a single upper bound is specified such that 
            #       signal <= upper bound =>(implies) pass
            #   * A size 3 tuple implies an upper and lower bound is specified such that
            #       lower bound <= signal <= upper bound =>(implies) pass
            assert(isinstance(interval, tuple))
            assert((len(interval) == 2) or (len(interval) == 3))
            
            # The first element must be a list of size 1 or 2 indicating the x-axis bounds
            # of the interval.
            assert(isinstance(interval[0], list))
            assert((len(interval[0])) == 1 or (len(interval[0]) == 2))
                
            # If the second element is a tuple then must contain two lists 
            # describing the factors and powers of an arbitrary polynomial.
            if isinstance(interval[1], tuple):
                assert(len(interval[1]) == 2)
                assert(isinstance(interval[1][0], list))
                assert(isinstance(interval[1][1], list))
                assert(len(interval[1][0]) == len(interval[1][1]))
            
            elif not isinstance(interval[1], list):
                # If the second element is a list then it must be a simple 
                # polynomial of integer powers describing the shape of the bound.
                assert(isinstance(interval[1], list))
                
                
    def _evaluateBound (self, intervalBound, signalBaseline):
        
        def applyPowers (inputData, factorsPowers):
            outputData = numpy.zeros(inputData.size)
            for factor, power in zip(factorsPowers[0], factorsPowers[1]):
                thisOutput = factor * numpy.power(inputData, power)
                
                outputData += thisOutput
                
            return outputData
        
        baselineBound = None
        if isinstance(intervalBound, list):
            baselineBound = polynomial.polyval(signalBaseline, intervalBound)
        elif isinstance(intervalBound, tuple):
            baselineBound = applyPowers(signalBaseline, intervalBound)
        else:
            raise ValidationException('Bad type for interval bound')
        
        return baselineBound
    
    
    def _evaluateUpperBound (self, interval, signal):
                
        signalBaseline = signal[0]
        signalValues = signal[1]
            
        baselineInterval = interval[0]
        intervalBound = interval[1]
        
        baselineIndex = self._evaluateInterval(baselineInterval, signalBaseline)
        
        baselineBound = self._evaluateBound(intervalBound, signalBaseline[baselineIndex])
            
        return not any(signalValues[baselineIndex] > baselineBound)
    
    
    def _evaluateUpperLowerBound (self, interval, signal):
        signalBaseline = signal[0]
        signalValues = signal[1]
            
        baselineInterval = interval[0]
        upperIntervalBound = interval[1]
        lowerIntervalBound = interval[2]
    
        baselineIndex = self._evaluateInterval(baselineInterval, signalBaseline)
        
        upperBaselineBound = self._evaluateBound(upperIntervalBound, signalBaseline[baselineIndex])
        lowerBaselineBound = self._evaluateBound(lowerIntervalBound, signalBaseline[baselineIndex])
            
        return not (any(signalValues[baselineIndex] > upperBaselineBound) or any(signalValues[baselineIndex] < lowerBaselineBound))
    
    
    def _evaluateInterval (self, baselineInterval, signalBaseline):
        baselineIndex = numpy.array([])
        
        if len(baselineInterval) == 1:
            # The interval is open ended
            intervalLowerBound = float(baselineInterval[0])
            baselineIndex = signalBaseline >= intervalLowerBound
            
        elif len(baselineInterval) == 2:
            # The interval is finite
            intervalLowerBound = float(baselineInterval[0])
            intervalUpperBound = float(baselineInterval[1])
            
            baselineIndex = numpy.logical_and((signalBaseline >= intervalLowerBound), (signalBaseline < intervalUpperBound))
            
        else:
            raise ValidationException('Incorrect number of interval elements, ' + repr(len(baselineInterval)))
            
        return baselineIndex
    
    
    def _plotIntervalUpperBound (self, interval, kwargs):
        assert(len(interval) == 2)
        
        baselineInterval = interval[0]
        upperIntervalBoundCoefficients = interval[1]
        
        self._plotIntervalBound(baselineInterval, upperIntervalBoundCoefficients, kwargs)
    
    
    def _plotIntervalUpperLowerBound (self, interval, kwargs):
        # Assume the current figure is the correct one
        assert(len(interval) == 3)
        
        baselineInterval = interval[0]
        upperIntervalBoundCoefficients = interval[1]
        lowerIntervalBoundCoefficients = interval[2]
        
        self._plotIntervalBound(baselineInterval, upperIntervalBoundCoefficients, kwargs)
        self._plotIntervalBound(baselineInterval, lowerIntervalBoundCoefficients, kwargs)
        

    def _plotIntervalBound (self, baselineInterval, intervalBoundCoefficients, kwargs):
        assert((len(baselineInterval) == 1) or (len(baselineInterval) == 2))
        
        numberPoints = None
        if isinstance(intervalBoundCoefficients, list):
            numberPoints = max([2, (2 * (2 * (len(intervalBoundCoefficients) - 1)))])
        elif isinstance(intervalBoundCoefficients, tuple):
            # This is necessarily a bit more complicated because the polynomial 
            # may now be of arbitrary powers, including fractional powers.
            powers = numpy.abs(numpy.array(intervalBoundCoefficients[1]))
            
            order = max([ max(powers[powers > 0]), max(1 / powers[powers > 0]) ])
            assert(order >= 1)
            numberPoints = max([2, (2 * (2 * order))])
        else:
            raise ValidationException('Incorrect type of interval elements, ' + repr(len(baselineInterval)))
        
        xLimits = self._getPlotIntervalXlimits(baselineInterval)
        
        xData = numpy.linspace(xLimits[0], xLimits[1], numberPoints)
        yData = self._evaluateBound(intervalBoundCoefficients, xData)
        
        # Assume the current figure is the correct one
        if not kwargs:
            mpp.plot(xData, yData, 'b-')
        else:
            mpp.plot(xData, yData, **kwargs)
            
        
    def _getPlotIntervalXlimits (self, baselineInterval):
        assert((len(baselineInterval) == 1) or (len(baselineInterval) == 2))
        
        xData = []
        if len(baselineInterval) == 1:
            # Use the current axis limit for the upper x-axis plot bound
            currentAxis = mpp.gca()
            
            xData = [baselineInterval[0] ]
            figureXLimits = currentAxis.get_xlim()
            xData.append(figureXLimits[1])
            
        elif len(baselineInterval) == 2:
            xData = baselineInterval
            
        else:
            raise ValidationException('Wrong length of interval, ' + repr(len(baselineInterval)))
            
        return xData
    