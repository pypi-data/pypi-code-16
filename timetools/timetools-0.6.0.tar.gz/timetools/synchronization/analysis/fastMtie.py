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
import multiprocessing as mtp
from operator import itemgetter

import timetools.signalProcessing.jobQueue as tsj
import timetools.synchronization.analysis.ituTG810 as sag810
import timetools.synchronization.analysis.mtieKernels as samk
import timetools.synchronization.intervals as si
     
     
def calculateMtie (localTime, referenceTime, samplingInterval, desiredNumberObservations, maximumNumberWorkers = mtp.cpu_count()):
    assert(len(localTime) > 1)
    assert(len(referenceTime) > 1)
    assert(localTime.size == referenceTime.size)
    
    timeError = sag810.calculateTimeError(localTime, referenceTime)

    maxIntervalIndex = len(localTime) - 1
    
    intervalIndex = si.generateMonotonicLogScale(numpy.floor(si.generateLogIntervalScale(1, maxIntervalIndex, desiredNumberObservations)))
    
    mtie = numpy.array([])
    if maximumNumberWorkers == 1:
        mtie = _calculateSingleProcessMtie(timeError, intervalIndex)
    else:
        neededNumberWorkers = min([maximumNumberWorkers, len(intervalIndex)])
        mtie = _calculateMultiprocessMtie(timeError, intervalIndex, neededNumberWorkers)
    
    observationIntervals = samplingInterval * intervalIndex
    
    return (mtie, observationIntervals)


class _mtieWorker (object):
    
    def __init__ (self, timeError, kernel = samk.smartWindow):
        self._timeError = timeError
        self._kernel = kernel


    def __call__ (self, thisInterval):
        thisMtie = self._kernel(self._timeError, thisInterval)
        
        return (thisMtie, thisInterval)


def _calculateMultiprocessMtie (timeError, intervalIndex, neededNumberWorkers):
    numberIntervals = len(intervalIndex)
    
    thisMtieWorker = _mtieWorker(timeError)
    
    thisPool = tsj.NoDaemonPool(neededNumberWorkers) 
    mtieResults = thisPool.map(thisMtieWorker, intervalIndex)

    assert(len(mtieResults) == numberIntervals)
    
    mtieResults.sort(key=itemgetter(1))

    mtie, sortedIntervalResults = map(list, zip(*mtieResults))
    
    assert(all(sortedIntervalResults == intervalIndex))
    
    return numpy.array(mtie)


def _calculateSingleProcessMtie (timeError, intervalIndex):
    '''
    Calculate Maximum Time Interval Error (MTIE) of two timebases using a 
    window step method, assuming they are identically, uniformly sampled.
    
    This is much faster to compute than the direct method.
    
    Assume localTime and referenceTime are numpy arrays.
    '''
    numberIntervals = len(intervalIndex)
    
    mtie = numpy.zeros(numberIntervals)
    
    for k in numpy.arange(0, numberIntervals):
        thisInterval = intervalIndex[k]
        
        mtie[k] = samk.smartWindow(timeError, thisInterval)
            
    return numpy.array(mtie)
    