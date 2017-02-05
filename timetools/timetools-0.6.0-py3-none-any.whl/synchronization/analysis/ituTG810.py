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

import timetools.synchronization.analysis.mtieKernels as samk
import timetools.synchronization.analysis.tdevKernels as satk
import timetools.synchronization.intervals as si


def calculateTimeError (localTime, referenceTime):
    '''
    Calculate Time Error (TE) of two timebases assuming they are identically, uniformly sampled.
    
    Assume localTime and referenceTime are numpy arrays.
    
    "Definitions and terminology for synchronization networks", ITU-T G.810 (08/96), Section 4.5.13, pp7
    '''
    assert(localTime.size == referenceTime.size)
    
    return(localTime - referenceTime)


def calculateTimeIntervalError (localTime, referenceTime, intervalSamples):
    '''
    Calculate Time Interval Error (TIE) of two timebases assuming they are identically, uniformly sampled.
    
    Assume localTime and referenceTime are numpy arrays.
    
    "Definitions and terminology for synchronization networks", ITU-T G.810 (08/96), Section 4.5.14, pp7
    '''
    assert(localTime.size == referenceTime.size)
    timeError = calculateTimeError(localTime, referenceTime)
    
    return(timeError[intervalSamples:timeError.size:1] - timeError[0:(timeError.size - intervalSamples):1])


def calculateMtie (localTime, referenceTime, samplingInterval, desiredNumberObservations):
    '''
    Calculate Maximum Time Interval Error (MTIE) of two timebases using the 
    direct method, assuming they are identically, uniformly sampled.
    
    "Definitions and terminology for synchronization networks", ITU-T G.810 (08/96), Section 4.5.15, pp7
    
    The ITU definition does a direct calculation on all windows sizes, but here a logarithmic scale is used 
    to improve computational efficiency slightly.
    
    Assume localTime and referenceTime are numpy arrays.
    '''
    assert(len(localTime) > 1)
    assert(len(referenceTime) > 1)
    assert(localTime.size == referenceTime.size)
    
    timeError = calculateTimeError(localTime, referenceTime)

    maxIntervalIndex = len(localTime) - 1
    
    intervalIndex = si.generateMonotonicLogScale(numpy.floor(si.generateLogIntervalScale(1, maxIntervalIndex, desiredNumberObservations)))
    mtie = numpy.zeros(intervalIndex.size)
    
    for k in numpy.arange(0, len(intervalIndex)):
        thisInterval = intervalIndex[k]
        
        mtie[k] = samk.slidingWindow(timeError, thisInterval)
    
    observationIntervals = samplingInterval * intervalIndex

    return (mtie, observationIntervals)


def calculateTdev (localTime, referenceTime, samplingInterval, desiredNumberObservations, kernel = satk.mean):
    assert(len(localTime) > 1)
    assert(len(referenceTime) > 1)
    assert(referenceTime.size == localTime.size)

    # Assume the signal is uniformly sampled.
    timeError = calculateTimeError(localTime, referenceTime)

    numberErrorPoints = len(timeError)
    rawTdevSize = math.floor(numberErrorPoints / 3)
    maxIntervalIndex = rawTdevSize

    intervalIndex = si.generateMonotonicLogScale(numpy.floor(si.generateLogIntervalScale(1, maxIntervalIndex, desiredNumberObservations)))
    
    # ITU-T Rec. G.810 (08/96) pp 17
    rawTdev = numpy.zeros(rawTdevSize)
    for n in (numpy.arange(0, rawTdevSize) + 1):
        iterationSize = numberErrorPoints - (3 * n) + 1
        tdevFactor = 1 / (6 * iterationSize)
        
        tdevSum = 0
        for j in (numpy.arange(0, iterationSize) + 1):
            tdevSum += numpy.power(kernel(timeError, n, j), 2)
        
        rawTdev[n - 1] = math.sqrt(tdevFactor * tdevSum)
    
    # Reduce the resolution to that specified
    # In the case of the direct TDEV method, this doesn't improve computation time, but it does improve memory usage
    tdev = rawTdev[intervalIndex - 1]
    
    observationIntervals = samplingInterval * intervalIndex
    
    return (tdev, observationIntervals)


def adevKernel (timeError, n):
    numberPoints = len(timeError)
    baseIndex = numpy.arange(0, (numberPoints - (2 * n)))
    
    error1 = timeError[baseIndex + (2 * n)]
    error2 = 2 * timeError[baseIndex + n]
    error3 = timeError[baseIndex]
    
    thisSum = numpy.sum(error1 - error2 + error3)
    
    return thisSum


def calculateAdev (localTime, referenceTime, samplingInterval, desiredNumberObservations):
    assert(len(localTime) > 1)
    assert(len(referenceTime) > 1)
    assert(referenceTime.size == localTime.size)

    # Assume the signal is uniformly sampled.
    timeError = calculateTimeError(localTime, referenceTime)

    numberErrorPoints = len(timeError)
    rawAdevSize = math.floor((numberErrorPoints - 1) / 2)
    maxIntervalIndex = rawAdevSize

    intervalIndex = si.generateMonotonicLogScale(numpy.floor(si.generateLogIntervalScale(1, maxIntervalIndex, desiredNumberObservations)))
    
    # ITU-T Rec. G.810 (08/96), Appendix II.1, pp 14
    rawAdev = numpy.zeros(rawAdevSize)
    for n in (numpy.arange(0, rawAdevSize) + 1):
        iterationSize = numberErrorPoints - (2 * n)
        adevFactor = 1 / (2 * numpy.power((n * samplingInterval), 2) * iterationSize)
        
        adevSum = numpy.power(adevKernel(timeError, n), 2)
        
        rawAdev[n - 1] = math.sqrt(adevFactor * adevSum)
    
    # Reduce the resolution to that specified
    # In the case of the direct ADEV method, this doesn't improve computation time, but it does improve memory usage
    adev = rawAdev[intervalIndex - 1]
    
    observationIntervals = samplingInterval * intervalIndex
    
    return (adev, observationIntervals)


def calculateMdev (localTime, referenceTime, samplingInterval, desiredNumberObservations):
    assert(len(localTime) > 1)
    assert(len(referenceTime) > 1)
    assert(referenceTime.size == localTime.size)
    
    tdev, observationIntervals = calculateTdev(localTime, referenceTime, samplingInterval, desiredNumberObservations)
    
    # ITU-T Rec. G.810 (08/96), Appendix II.2, pp 15
    # ITU-T Rec. G.810 (08/96), Appendix II.3, pp 16
    mdev = (numpy.sqrt(3) / observationIntervals) * tdev
    
    return (mdev, observationIntervals)


def tieRmsKernel(timeError, n):
    numberPoints = len(timeError)
    baseIndex = numpy.arange(0, (numberPoints - n))
    
    error1 = timeError[baseIndex + n]
    error2 = timeError[baseIndex]
    
    thisSum = numpy.sum(numpy.power((error1 - error2), 2))
    
    return thisSum
    

def calculateTieRms (localTime, referenceTime, samplingInterval, desiredNumberObservations):
    assert(len(localTime) > 1)
    assert(len(referenceTime) > 1)
    assert(referenceTime.size == localTime.size)

    # Assume the signal is uniformly sampled.
    timeError = calculateTimeError(localTime, referenceTime)

    numberErrorPoints = len(timeError)
    rawTieRmsSize = numberErrorPoints - 1
    maxIntervalIndex = rawTieRmsSize

    intervalIndex = si.generateMonotonicLogScale(numpy.floor(si.generateLogIntervalScale(1, maxIntervalIndex, desiredNumberObservations)))
    
    # ITU-T Rec. G.810 (08/96), Appendix II.4, pp 18
    rawTieRms = numpy.zeros(rawTieRmsSize)
    for n in (numpy.arange(0, rawTieRmsSize) + 1):
        iterationSize = numberErrorPoints - n
        tieRmsFactor = 1 / iterationSize
        
        tieRmsSum = tieRmsKernel(timeError, n)
        
        rawTieRms[n - 1] = math.sqrt(tieRmsFactor * tieRmsSum)
    
    # Reduce the resolution to that specified
    # In the case of the direct TIE rms method, this doesn't improve computation time, but it does improve memory usage
    tieRms = rawTieRms[intervalIndex - 1]
    
    observationIntervals = samplingInterval * intervalIndex
    
    return (tieRms, observationIntervals)


def calculateTvar (localTime, referenceTime, samplingInterval, desiredNumberObservations):
    tdev, observationIntervals = calculateTdev(localTime, referenceTime, samplingInterval, desiredNumberObservations)
    
    tvar = numpy.power(tdev, 2)
    
    return (tvar, observationIntervals)
