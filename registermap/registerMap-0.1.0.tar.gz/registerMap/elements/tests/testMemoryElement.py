#
# Copyright 2016 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import unittest

import registerMap.elements.element as rml


log = logging.getLogger( __name__ )


class TestDefaultConstructor( unittest.TestCase ) :
    def testDefaultArguments( self ) :
        testElement = rml.MemoryElement( )

        self.assertIsNone( testElement.startAddress )
        self.assertIsNone( testElement.endAddress )
        self.assertEqual( testElement.sizeMemoryUnits, 0 )


    def testAssignStartAddressWithNoneSizeEnd( self ) :
        testElement = rml.MemoryElement( )

        testElement.startAddress = 2
        testElement.sizeMemoryUnits = None

        self.assertEqual( testElement.startAddress, 2 )
        self.assertIsNone( testElement.endAddress )
        self.assertIsNone( testElement.sizeMemoryUnits )


    def testNoneSizeEndThenAssignStartAddress( self ) :
        testElement = rml.MemoryElement( )

        testElement.sizeMemoryUnits = None
        testElement.startAddress = 2

        self.assertEqual( testElement.startAddress, 2 )
        self.assertIsNone( testElement.endAddress )
        self.assertIsNone( testElement.sizeMemoryUnits )


    def testValidStartAddressArgument( self ) :
        expectedValue = 0x10
        testElement = rml.MemoryElement( startAddress = expectedValue )

        self.assertEqual( testElement.startAddress, expectedValue )
        self.assertEqual( testElement.endAddress, expectedValue )
        self.assertEqual( testElement.sizeMemoryUnits, 1 )


    def testValidStartEndAddressArguments( self ) :
        expectedStartAddress = 0x10
        expectedEndAddress = 0x15
        testElement = rml.MemoryElement( startAddress = expectedStartAddress,
                                         endAddress = expectedEndAddress )

        self.assertEqual( testElement.startAddress, expectedStartAddress )
        self.assertEqual( testElement.endAddress, expectedEndAddress )
        self.assertEqual( testElement.sizeMemoryUnits, (expectedEndAddress - expectedStartAddress + 1) )


    def testValidStartAddressSizeArguments( self ) :
        expectedStartAddress = 0x10
        expectedSize = 5
        testElement = rml.MemoryElement( startAddress = expectedStartAddress,
                                         sizeMemoryUnits = expectedSize )

        self.assertEqual( testElement.startAddress, expectedStartAddress )
        self.assertEqual( testElement.sizeMemoryUnits, expectedSize )
        self.assertEqual( testElement.endAddress, (expectedStartAddress + expectedSize - 1) )


    def testSpecifyBothEndAddressAndSizeRaises( self ) :
        with self.assertRaisesRegex( rml.ConfigurationError, '^Cannot specify both endAddress and sizeMemoryUnits' ) :
            rml.MemoryElement( endAddress = 4,
                               sizeMemoryUnits = 6 )


class TestMemoryElementStartAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.testElement = rml.MemoryElement( )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testElement.startAddress )


    def testAssignValueNoSize( self ) :
        expectedValue = 0x10
        self.assertNotEqual( self.testElement.startAddress, expectedValue )

        self.testElement.startAddress = expectedValue

        self.assertEqual( self.testElement.startAddress, expectedValue )
        self.assertEqual( self.testElement.endAddress, self.testElement.startAddress )


    def testAssignValueSizeDefined( self ) :
        self.testElement.sizeMemoryUnits = 5

        expectedStartAddress = 0x10
        self.assertNotEqual( self.testElement.startAddress, expectedStartAddress )
        expectedEndAddress = 0x14
        self.assertNotEqual( self.testElement.endAddress, expectedEndAddress )

        self.testElement.startAddress = expectedStartAddress

        self.assertEqual( self.testElement.startAddress, expectedStartAddress )
        self.assertEqual( self.testElement.endAddress, expectedEndAddress )


    def testAssignValueWithEndAddress( self ) :
        initialStartAddress = 0x10
        self.assertNotEqual( self.testElement.startAddress, initialStartAddress )

        self.testElement.startAddress = initialStartAddress
        self.testElement.sizeMemoryUnits = 5

        expectedStartAddress = 0x10
        self.testElement.startAddress = expectedStartAddress

        log.debug( 'Size after start address change: ' + repr( self.testElement.sizeMemoryUnits ) )

        self.assertEqual( self.testElement.startAddress, expectedStartAddress )
        self.assertEqual( self.testElement.endAddress, (expectedStartAddress + self.testElement.sizeMemoryUnits - 1) )


    def testUnassignedStartAddressRaises( self ) :
        testElement = rml.MemoryElement( )
        with self.assertRaisesRegex( rml.ConfigurationError,
                                     '^Must define start address before attempting to define end address' ) :
            testElement.endAddress = 0x5


    def testAssignNone( self ) :
        expectedValue = 0x10
        self.testElement.startAddress = expectedValue
        self.assertEqual( self.testElement.startAddress, expectedValue )

        self.testElement.startAddress = None

        self.assertIsNone( self.testElement.startAddress )
        self.assertIsNone( self.testElement.endAddress )


class TestMemoryElementEndAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.testElement = rml.MemoryElement( )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testElement.endAddress )


    def testAssignValue( self ) :
        self.testElement.startAddress = 0x10
        expectedEndAddress = 0x20
        self.assertNotEqual( self.testElement.endAddress, expectedEndAddress )

        self.testElement.endAddress = expectedEndAddress

        self.assertEqual( self.testElement.endAddress, expectedEndAddress )
        self.assertEqual( self.testElement.sizeMemoryUnits, (expectedEndAddress - self.testElement.startAddress + 1) )


class TestMemoryElementSize( unittest.TestCase ) :
    def setUp( self ) :
        self.testElement = rml.MemoryElement( )


    def testDefaultValue( self ) :
        self.assertEqual( self.testElement.sizeMemoryUnits, 0 )


    def testValueAfterInitialStartAddressAssign( self ) :
        self.testElement.startAddress = 0x10

        self.assertEqual( self.testElement.sizeMemoryUnits, 1 )


    def testAssignValue( self ) :
        self.testElement.startAddress = 0x10
        expectedSize = 5
        self.assertNotEqual( self.testElement.sizeMemoryUnits, expectedSize )

        self.testElement.sizeMemoryUnits = expectedSize

        self.assertEqual( self.testElement.sizeMemoryUnits, expectedSize )
        self.assertEqual( self.testElement.endAddress,
                          (self.testElement.startAddress + self.testElement.sizeMemoryUnits - 1) )


    def testPrematureAssignmentNoRaise( self ) :
        self.assertIsNone( self.testElement.startAddress )
        self.assertIsNone( self.testElement.endAddress )

        expectedValue = 5
        self.testElement.sizeMemoryUnits = expectedValue

        self.assertEqual( self.testElement.sizeMemoryUnits, expectedValue )


if __name__ == '__main__' :
    unittest.main( )
