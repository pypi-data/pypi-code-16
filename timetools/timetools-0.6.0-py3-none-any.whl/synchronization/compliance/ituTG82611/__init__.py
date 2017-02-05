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

import matplotlib.pyplot as mpp
import multiprocessing as mtp
import numpy

import timetools.signalProcessing.jobQueue as tsj

    
def calculateFloorPacketPercent( pdvMicroseconds, thisClusterRangeThresholdMicroseconds ):
    windowFloorDelayMicroseconds = numpy.min( pdvMicroseconds )
    clusterPeakMicroseconds = windowFloorDelayMicroseconds + thisClusterRangeThresholdMicroseconds
    
    floorClusterPdv = ( pdvMicroseconds >= windowFloorDelayMicroseconds ) & ( pdvMicroseconds <= clusterPeakMicroseconds )
    
    numberFloorCluster = floorClusterPdv.sum()
    
    numberWindowElements = len( pdvMicroseconds )
    
    floorPacketPercent = numberFloorCluster / numberWindowElements * 100
    
    return floorPacketPercent
    
    
def calculateClusterPeak( pdvMicroseconds, thisFloorPacketPercentThreshold ):
    windowFloorDelayMicroseconds = numpy.min( pdvMicroseconds )
    
    numberWindowElements = len( pdvMicroseconds )
    numberClusterPackets = int( numpy.floor( ( thisFloorPacketPercentThreshold / 100 ) * numberWindowElements ) )
    
    sortedUniquePdvMicroseconds = numpy.unique( pdvMicroseconds )
    
    clusterThresholdPdvMicrosecond = sortedUniquePdvMicroseconds[ numberClusterPackets ]
    
    clusterPeakPdv = clusterThresholdPdvMicrosecond - windowFloorDelayMicroseconds
    
    return clusterPeakPdv
        

class _Worker( object ):
    
    def __init__ ( self, 
                   timebaseSeconds, 
                   pdvMicroseconds, 
                   floorPacketPercentThreshold, 
                   clusterRangeThresholdMicroseconds,
                   windowDurationSeconds ):
        self._timebaseSeconds = timebaseSeconds
        self._pdvMicroseconds = pdvMicroseconds
        self._floorPacketPercentThreshold = floorPacketPercentThreshold
        self._clusterRangeThresholdMicroseconds = clusterRangeThresholdMicroseconds
        self._windowDurationSeconds = windowDurationSeconds


    def __call__ ( self, thisIntervalIndex ):
        pdvAnalysis = []
        for thisIndex, resultIndex in zip( thisIntervalIndex, range(0, len( thisIntervalIndex ) ) ):
            lowerWindowBoundSeconds = self._timebaseSeconds[ thisIndex ]
            upperWindowBoundSeconds = lowerWindowBoundSeconds + self._windowDurationSeconds
            windowTimeIndex = ( self._timebaseSeconds >= lowerWindowBoundSeconds ) \
                & ( self._timebaseSeconds < upperWindowBoundSeconds )
            windowPdvMicroseconds = self._pdvMicroseconds[ windowTimeIndex ]
        
            calculatedFloorPacketPercent = calculateFloorPacketPercent( windowPdvMicroseconds, 
                                                                                     self._clusterRangeThresholdMicroseconds )
            calculatedClusterPeakMicroseconds = calculateClusterPeak( windowPdvMicroseconds, 
                                                                                   self._floorPacketPercentThreshold )
            pdvAnalysis.append( ( calculatedFloorPacketPercent, calculatedClusterPeakMicroseconds ) )
        
        return ( thisIntervalIndex, pdvAnalysis )
    

def scatterIndices( indexArray, numberGroups ):
    '''
        Split the array of indices into groups for multiprocessing.
        
        Assume that the number of groups cannot necessarily be divided evenly 
        across the array.
    '''
    
    # numpy.array_split returns a float array so need to restore it to int for indexing.
    floatSplitIndices = numpy.array_split( indexArray, numberGroups )
    
    splitIndices = [ x.astype(int) for x in floatSplitIndices ]
    
    return splitIndices

def _calculateResultSize( thisSplitResult ):
    thisSize = 0
    for thisResult in thisSplitResult:
        thisSize += len( thisResult[0] )
        
    return thisSize


def gatherResults( splitResultArray ):
    '''
        Assume splitResultArray is an iterable of tuples. The first element of 
        tuples is the group of indices calculated. The second element is a 
        result of arbitrary type.
    '''
    arraySize = _calculateResultSize( splitResultArray )
    
    resultArray = [ () for i in range( 0, arraySize ) ]
    orderedIndexArray = numpy.zeros( arraySize )
    for thisResult in splitResultArray:
        groupIndices = thisResult[0]
        groupResults = thisResult[1]
        
        for i in range(0, len( groupIndices ) ):
            resultArray[ groupIndices[ i ] ] = groupResults[ i ]
        
        orderedIndexArray[ groupIndices ] = groupIndices
        
    return ( resultArray, orderedIndexArray )


def evaluatePdvNetworkLimits( measurementTimeSeconds, 
                              pdvMagnitudeMicroseconds, 
                              neededNumberWorkers = mtp.cpu_count() ):
    
    windowDurationSeconds = 200
    floorPacketPercentThreshold = 1
    clusterRangeThresholdMicroseconds = 150
    
    endIndex = numpy.searchsorted( measurementTimeSeconds, 
                                   ( measurementTimeSeconds[ -1 ] - windowDurationSeconds ) )
    
    indices = numpy.arange( 0, endIndex )
    
    splitIndices = scatterIndices( indices, neededNumberWorkers )
    
    thisWorker = _Worker( measurementTimeSeconds, 
                          pdvMagnitudeMicroseconds, 
                          floorPacketPercentThreshold, 
                          clusterRangeThresholdMicroseconds,
                          windowDurationSeconds )
    
    thisPool = tsj.NoDaemonPool( neededNumberWorkers ) 
    splitResults = thisPool.map( thisWorker, splitIndices )

    assert( len( splitResults ) == len( splitIndices ) )
    
    results, orderedIndex = gatherResults( splitResults )
    
    assert( len( results ) == len( indices ) )
    assert( len( orderedIndex ) == len( indices ) )
    assert( numpy.all( indices == orderedIndex ) )
    
    calculatedFloorPacketPercent = numpy.array( [ x[0] for x in results ] )
    calculatedClusterPeakMicroseconds = numpy.array( [ x[1] for x in results ] )
    
    return ( numpy.all( calculatedFloorPacketPercent >= floorPacketPercentThreshold ), 
             numpy.all( calculatedClusterPeakMicroseconds < clusterRangeThresholdMicroseconds ), 
             calculatedFloorPacketPercent, 
             calculatedClusterPeakMicroseconds )
        