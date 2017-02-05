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
import random
import unittest

import timetools.synchronization.compliance.ituTG82611 as tscg82611


class TestItuTG82611( unittest.TestCase ):
    
    def _generateSplitResult( self, splitIndices, results ):
        # Assume results is a numeric array
        splitResults = []
        for thisGroup in splitIndices:
            splitResults.append( ( thisGroup, results[ thisGroup ] ) )
            
        return splitResults
    
    def _generateSplitResult2( self, splitIndices, results ):
        # Assume results is an array of abitrary type elements
        splitResults = []
        for thisGroup in splitIndices:
            resultGroup = []
            for thisIndex in thisGroup:
                resultGroup.append( results[ thisIndex ] )
                
            splitResults.append( ( thisGroup, resultGroup ) )
            
        return splitResults
        

    def testCalculateFloorPacketPercent( self ):
        threshold = 5
        expected = 6
        
        pdv = numpy.arange( 0, 100, 1 )
        result = tscg82611.calculateFloorPacketPercent( pdv, threshold )
        
        self.assertTrue( ( result == expected ), "Bad floor packet percent: " + repr( expected ) + "(expected), " + repr( result ) + "(actual)" )
        
        
    def testCalculateClusterPeak( self ):
        threshold = 4
        expected = 4
    
        pdv = numpy.arange( 0, 100, 1 )
        result = tscg82611.calculateClusterPeak( pdv, threshold )
        
        self.assertTrue( ( result == expected ), "Bad cluster peak: " + repr( expected ) + "(expected), " + repr( result ) + "(actual)" )
        
        
    def testScatterIndices( self ):
        numberGroups = 4
        indices = numpy.arange( 0, 9 )
        
        splitIndices = tscg82611.scatterIndices( indices, numberGroups )
        
        self.assertTrue( ( len( splitIndices ) == numberGroups ), 
                         "Wrong number of groups: " 
                         + str( len( splitIndices ) ) + "(actual), " 
                         + str( numberGroups ) + "(expected)" )
        
        
    def testCalculateResultSize( self ):
        numberGroups = 4
        indices = numpy.arange( 0, 9 )
        results = indices + 14
        
        expectedResultSize = len( indices )
        
        splitIndices = tscg82611.scatterIndices( indices, numberGroups )
        
        splitResult = self._generateSplitResult( splitIndices, results )
        
        actualResultSize = tscg82611._calculateResultSize( splitResult )
        
        
        self.assertTrue( ( actualResultSize == expectedResultSize ), 
                         "Wrong result size: " 
                         + str( actualResultSize ) + " (actual), " 
                         + str( expectedResultSize ) + " (expected)" )
        
        
    def testScatterGatherIndices1( self ):
        numberGroups = 4
        indices = numpy.arange( 0, 9 )
        expectedResults = indices + 14
        
        splitIndices = tscg82611.scatterIndices( indices, numberGroups )
        
        splitResults = self._generateSplitResult( splitIndices, expectedResults )
        
        ( actualResults, orderedIndexGroupArray ) = tscg82611.gatherResults( splitResults )
        
        self.assertTrue( ( numpy.all( expectedResults == actualResults ) ), 
                         "Unexpected results: \n  " 
                         + str( actualResults ) + " (actual)\n  " 
                         + str( expectedResults ) + " (expected)" )
        
        
    def testScatterGatherIndices2( self ):
        numberGroups = 4
        expectedIndices = numpy.arange( 0, 9 )
        expectedResults = expectedIndices + 14
        
        indices = random.sample( range( 0, len( expectedIndices ) ), len( expectedIndices ) )
        
        splitIndices = tscg82611.scatterIndices( indices, numberGroups )
        
        splitResults = self._generateSplitResult( splitIndices, expectedResults )
        
        ( actualResults, orderedIndex ) = tscg82611.gatherResults( splitResults )
        
        self.assertTrue( ( numpy.all( expectedResults == actualResults ) ), 
                         "Unexpected results: \n  " 
                         + str( actualResults ) + " (actual)\n  " 
                         + str( expectedResults ) + " (expected)" )
        
        self.assertTrue( ( numpy.all( expectedIndices == orderedIndex ) ), 
                         "Unexpected results: \n  " 
                         + str( orderedIndex ) + " (actual)\n  " 
                         + str( expectedIndices ) + " (expected)" )
        
        
    def testScatterGatherIndices3( self ):
        numberGroups = 4
        indices = numpy.arange( 0, 9 )
        expectedResults1 = indices + 14
        expectedResults2 = indices + 32
        
        expectedResults = [ ( x, y ) for x, y in zip( expectedResults1, expectedResults2 ) ]
        
        splitIndices = tscg82611.scatterIndices( indices, numberGroups )
        splitResults = self._generateSplitResult2( splitIndices, expectedResults )
        
        ( actualResults, orderedIndexGroupArray ) = tscg82611.gatherResults( splitResults )
        
        actualResult1 = numpy.array( [ x[0] for x in actualResults ] )
        actualResult2 = numpy.array( [ x[1] for x in actualResults ] )
        
        self.assertTrue( ( numpy.all( expectedResults1 == actualResult1 ) ), 
                         "Unexpected results: \n  " 
                         + str( actualResult1 ) + " (actual)\n  " 
                         + str( expectedResults1 ) + " (expected)" )
        
        self.assertTrue( ( numpy.all( expectedResults2 == actualResult2 ) ), 
                         "Unexpected results: \n  " 
                         + str( actualResult2 ) + " (actual)\n  " 
                         + str( expectedResults2 ) + " (expected)" )


if __name__ == "__main__":
    unittest.main()
    