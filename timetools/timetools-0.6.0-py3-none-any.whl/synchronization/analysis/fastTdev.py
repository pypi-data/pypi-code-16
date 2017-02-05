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
import multiprocessing as mtp
import numpy
from operator import itemgetter

import timetools.signalProcessing.jobQueue as tsj
import timetools.synchronization.analysis.ituTG810 as sag810
import timetools.synchronization.analysis.tdevKernels as satk
import timetools.synchronization.intervals as si
     
     
def calculateTdev (localTime, 
                   referenceTime, 
                   samplingInterval, 
                   desiredNumberObservations, 
                   maximumNumberWorkers = mtp.cpu_count()):
    assert(len(localTime) > 1)
    assert(len(referenceTime) > 1)
    assert(localTime.size == referenceTime.size)
    
    # Assume the signal is uniformly sampled.
    timeError = sag810.calculateTimeError(localTime, referenceTime)

    numberErrorPoints = len(timeError)
    rawTdevSize = math.floor(numberErrorPoints / 3.0)
    maxIntervalIndex = rawTdevSize

    intervalIndex = si.generateMonotonicLogScale(numpy.floor(si.generateLogIntervalScale(1, maxIntervalIndex, desiredNumberObservations)))
    
    tdev = numpy.array([])
    if maximumNumberWorkers == 1:
        tdev = _calculateSingleProcessTdev(timeError, intervalIndex, rawTdevSize)
    else:
        neededNumberWorkers = min([maximumNumberWorkers, len(intervalIndex)])
        tdev = _calculateMultiprocessdev(timeError, intervalIndex, rawTdevSize, maximumNumberWorkers = neededNumberWorkers)
    
    observationIntervals = samplingInterval * intervalIndex
    
    return (tdev, observationIntervals)


def _calculateSingleProcessTdev (timeError, 
                                 intervalIndex, 
                                 rawTdevSize):
    '''
    For single process, a faster TDEV calculation than the G.810 direct method.
    '''
    numberErrorPoints = len(timeError)

    # "RAPID CALCULATION OF TIME DEVIATION AND MODIFIED ALLAN DEVIATION FOR
    # CHARACTERIZING TELECOMMUNICATIONS CLOCK STABILITY",
    #    Li, Liao, Hwang, International Journal of Computers and Applications, 
    #    Vol. 30, No. 2, 2008

    # Interval size n = 1 must be the first observation interval size
    j1Array = numpy.arange(0, (numberErrorPoints - 2))

    delta1j = timeError[j1Array] - (2.0 * timeError[j1Array + 1]) + timeError[j1Array + 2]
    # s(0, j) = 0, pp94
    s0j = 0;
    snj = s0j + delta1j;
    y = numpy.power(snj[j1Array], 2, dtype='float64') / (6.0 * (numberErrorPoints - 2))
    x = numpy.sum(y);

    rawTdev = numpy.zeros(rawTdevSize, dtype='float64')
    rawTdev[0] = math.sqrt(x)

    # Calculate the full resolution (sample by sample) TDEV
    for n in (numpy.arange(1, rawTdevSize) + 1):
        njArray = numpy.arange(0, (numberErrorPoints - (3 * n) + 1))
        
        deltanj = (3.0 * (timeError[n - 1 + njArray] - timeError[(2 * n) - 2 + njArray] - timeError[(2 * n) - 1 + njArray])) \
            + (timeError[(3 * n) - 3 + njArray] + timeError[(3 * n) - 2 + njArray] + timeError[(3 * n) - 1 + njArray])
        
        snj[njArray] += deltanj[njArray]
        y = numpy.power(snj[njArray], 2, dtype='float64') / ((6.0 * n * n) * (numberErrorPoints - (3.0 * n) + 1))
        x = numpy.sum(y)
        
        rawTdev[n - 1] = numpy.sqrt(x)
    
    # Reduce the resolution to that specified by the user
    tdev = rawTdev[intervalIndex - 1]
    
    return tdev


class _tdevWorker (object):
    
    def __init__ (self, timeError, kernel = satk.mean):
        self._timeError = timeError
        self._kernel = kernel


    def __call__ (self, thisInterval):
        iterationSize = self._timeError.size - (3 * thisInterval) + 1
        tdevFactor = 1 / (6.0 * iterationSize)
        
        tdevSum = 0
        for j in (numpy.arange(0, iterationSize) + 1):
            tdevSum += numpy.power(self._kernel(self._timeError, thisInterval, j), 2, dtype='float64')
        
        thisTdev = numpy.sqrt(tdevFactor * tdevSum)
        
        return (thisTdev, thisInterval)
     
     
def _calculateMultiprocessdev (timeError, 
                               intervalIndex, 
                               rawTdevSize, 
                               kernel = satk.mean, 
                               maximumNumberWorkers = mtp.cpu_count()):
    '''
    Use the direct TDEV kernel, but take advantage of the embarrassingly 
    parallel nature of the iteration over intervals.
    '''
    thisTdevWorker = _tdevWorker(timeError, kernel = kernel)
    
    neededNumberWorkers = min([maximumNumberWorkers, len(intervalIndex)])
    thisPool = tsj.NoDaemonPool(neededNumberWorkers)
    tdevResults = thisPool.map(thisTdevWorker, intervalIndex)
    
    tdevResults.sort(key=itemgetter(1))

    totalTdevList, totalSortedIntervalResultsList = map(list, zip(*tdevResults))
    totalTdev = numpy.array(totalTdevList, dtype='float64')
    totalSortedIntervalResults = numpy.array(totalSortedIntervalResultsList, dtype='int64')
    assert(len(totalTdev) == len(totalSortedIntervalResults))
    
    indexing = [i for i in numpy.arange(0, len(totalSortedIntervalResults)) for item in intervalIndex if totalSortedIntervalResults[i] == item]
    selectedTdev = totalTdev[indexing]
    selectedIntervalResults = totalSortedIntervalResults[indexing]

    assert(len(tdevResults) == len(intervalIndex))
    assert(all(selectedIntervalResults == intervalIndex))
    
    return numpy.array(selectedTdev)
