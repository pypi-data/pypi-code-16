"""
Unit tests for Register
"""
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

import collections
import logging
import unittest

import registerMap.elements.memory as rmm
import registerMap.elements.register as rmr
import registerMap.utility.observer as rmo
from registerMap.elements.tests.mockObserver import MockObserver


log = logging.getLogger( __name__ )


class MockPreviousRegister :
    def __init__( self,
                  startAddress = None,
                  endAddress = None,
                  sizeMemoryUnits = None ) :
        self.sizeChangeNotifier = rmo.Observable( )
        self.addressChangeNotifier = rmo.Observable( )

        self.__address = startAddress
        if (endAddress is not None) and (startAddress is not None) :
            self.__endAddress = endAddress
            self.__sizeMemoryUnits = self.__endAddress - self.__address + 1
        elif (sizeMemoryUnits is not None) and (startAddress is not None) :
            self.__sizeMemoryUnits = sizeMemoryUnits
            self.__endAddress = self.__address + self.__sizeMemoryUnits - 1
        elif (sizeMemoryUnits is not None) and (endAddress is not None) :
            self.__endAddress = endAddress
            self.__sizeMemoryUnits = sizeMemoryUnits
            self.__address = self.__endAddress - self.__sizeMemoryUnits + 1
        elif (startAddress is None) and (sizeMemoryUnits is not None or endAddress is not None) :
            raise RuntimeError( 'Must specify address if specifying end address or size' )
        else :
            self.__sizeMemoryUnits = None
            self.__endAddress = None


    @property
    def address( self ) :
        return self.__address


    @address.setter
    def address( self, value ) :
        if self.__address is not None :
            addressChange = value - self.__address
            self.__address = value
            self.__endAddress += addressChange
        else :
            self.__address = value
            self.__endAddress = self.__address + self.__sizeMemoryUnits - 1

        self.addressChangeNotifier.notifyObservers( )


    @property
    def endAddress( self ) :
        return self.__endAddress


    @endAddress.setter
    def endAddress( self, value ) :
        self.__endAddress = value
        # For the purpose of testing, assume that a change in end address always signals a size change.
        self.__sizeMemoryUnits = self.__endAddress - self.__address + 1
        self.sizeChangeNotifier.notifyObservers( )


    @property
    def sizeMemoryUnits( self ) :
        return self.__sizeMemoryUnits


    @sizeMemoryUnits.setter
    def sizeMemoryUnits( self, value ) :
        self.__sizeMemoryUnits = value
        self.__endAddress = self.__address + self.__sizeMemoryUnits - 1
        self.sizeChangeNotifier.notifyObservers( )


class TestRegisterAddressPreviousNoneAddress( unittest.TestCase ) :
    """
    Test register address when the previous address has no defined address or size.
    """


    def setUp( self ) :
        self.observer = MockObserver( )
        self.previousRegister = MockPreviousRegister( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.previousElement = self.previousRegister

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )
        self.testRegister.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testRegister.address )
        self.assertIsNone( self.testRegister.endAddress )


    def testFixedAddress( self ) :
        expectedValue = 0x15

        self.assertNotEqual( self.testRegister.address, expectedValue )

        self.testRegister[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        self.assertEqual( self.testRegister.address, expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )


    def testAlignedAddress( self ) :
        alignmentValue = 2

        self.testRegister[ 'constraints' ][ 'alignmentMemoryUnits' ] = alignmentValue

        # Attempt to constrain alignment with no concrete addresses does nothing
        self.assertIsNone( self.testRegister.address )
        self.assertIsNone( self.testRegister.endAddress )
        self.assertEqual( self.observer.updateCount, 0 )


class TestRegisterAddressPreviousConcreteAddress( unittest.TestCase ) :
    """
    Test register address when the previous register has concrete address and size.
    """


    def setUp( self ) :
        self.observer = MockObserver( )
        self.previousRegister = MockPreviousRegister( startAddress = 0x10,
                                                      sizeMemoryUnits = 5 )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.previousElement = self.previousRegister

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )
        self.testRegister.addressChangeNotifier.addObserver( self.observer )


    def testFixedAddress( self ) :
        expectedValue = 0x16

        self.assertNotEqual( self.testRegister.address, expectedValue )

        self.testRegister[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        self.assertEqual( self.testRegister.address, expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )


    def testFixedAddressOnPreviousRaises( self ) :
        expectedValue = self.previousRegister.endAddress

        with self.assertRaisesRegex( rmr.ConstraintError, '^Fixed address exceeded' ) :
            self.testRegister[ 'constraints' ][ 'fixedAddress' ] = expectedValue


    def testAlignedAddress( self ) :
        alignmentValue = 2
        expectedValue = self.previousRegister.endAddress + 2

        self.assertEqual( (expectedValue % alignmentValue), 0 )
        self.assertLess( self.testRegister.address, expectedValue )

        self.testRegister[ 'constraints' ][ 'alignmentMemoryUnits' ] = alignmentValue

        self.assertEqual( self.testRegister.address, expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )


class TestRegisterBitFields( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertEqual( self.testRegister[ 'bitFields' ], collections.OrderedDict( ) )


    def testAddSmallBitField( self ) :
        self.assertEqual( self.testRegister.memory.memoryUnitBits, 8 )
        expectedName = 'bitFieldName'
        expectedBitRange = [ 0, 4 ]
        self.assertEqual( len( self.testRegister[ 'bitFields' ] ), 0 )

        returnValue = self.testRegister.addBitField( expectedName, expectedBitRange )

        self.assertEqual( len( self.testRegister[ 'bitFields' ] ), 1 )
        self.assertEqual( self.testRegister[ 'bitFields' ][ expectedName ][ 'name' ], expectedName )
        self.assertEqual( self.testRegister[ 'bitFields' ][ expectedName ][ 'bitRange' ], expectedBitRange )

        # The expected notifications is zero because the register initially has size 1 and the bit range doesn't change that.
        self.assertEqual( self.observer.updateCount, 0 )

        # addBitField returns the created BitField object
        self.assertEqual( returnValue, self.testRegister[ 'bitFields' ][ expectedName ] )


    def testAddLargeBitField( self ) :
        self.assertEqual( self.testRegister.memory.memoryUnitBits, 8 )
        expectedName = 'bitFieldName'
        expectedBitRange = [ 0, 10 ]
        self.assertEqual( len( self.testRegister[ 'bitFields' ] ), 0 )

        returnValue = self.testRegister.addBitField( expectedName, expectedBitRange )

        self.assertEqual( len( self.testRegister[ 'bitFields' ] ), 1 )
        self.assertEqual( self.testRegister[ 'bitFields' ][ expectedName ][ 'name' ], expectedName )
        self.assertEqual( self.testRegister[ 'bitFields' ][ expectedName ][ 'bitRange' ], expectedBitRange )

        # The expected notifications is one because the bit range assignment changes the number of memory units to two.
        self.assertEqual( self.observer.updateCount, 1 )

        # addBitField returns the created BitField object
        self.assertEqual( returnValue, self.testRegister[ 'bitFields' ][ expectedName ] )


    def testMultipleBitFields( self ) :
        self.assertEqual( self.testRegister.memory.memoryUnitBits, 8 )

        expectedFieldParameters = { 'field1' : [ 0, 2 ],
                                    'field2' : [ 3, 6 ],
                                    'field3' : [ 7, 7 ] }

        for name, bitRange in expectedFieldParameters.items( ) :
            self.testRegister.addBitField( name, bitRange )

        self.assertEqual( len( self.testRegister[ 'bitFields' ] ), len( expectedFieldParameters ) )

        for name, bitRange in expectedFieldParameters.items( ) :
            self.assertEqual( self.testRegister[ 'bitFields' ][ name ][ 'name' ],
                              name )
            self.assertEqual( self.testRegister[ 'bitFields' ][ name ][ 'bitRange' ],
                              bitRange )


    def testAddDuplicateNameRaises( self ) :
        expectedName = 'bitFieldName'
        expectedBitRange = [ 0, 4 ]
        self.testRegister.addBitField( expectedName, expectedBitRange )

        self.assertEqual( len( self.testRegister[ 'bitFields' ] ), 1 )
        self.assertEqual( self.testRegister[ 'bitFields' ][ expectedName ][ 'name' ], expectedName )
        self.assertEqual( self.testRegister[ 'bitFields' ][ expectedName ][ 'bitRange' ], expectedBitRange )

        with self.assertRaisesRegex( rmr.ConfigurationError, '^Created bit field names must be unique' ) :
            self.testRegister.addBitField( expectedName, [ 5, 7 ] )


    def testMultipleBitFieldsAddedToArbitrarySizeWithoutConstraint( self ) :
        self.assertEqual( self.testRegister.memory.memoryUnitBits, 8 )
        self.assertEqual( len( self.testRegister[ 'bitFields' ] ), 0 )

        self.testRegister.addBitField( 'testField1', [ 0, 3 ] )
        self.testRegister.addBitField( 'testField2', [ 4, 10 ] )
        self.testRegister.addBitField( 'testField3', [ 11, 25 ] )

        self.assertEqual( self.testRegister.sizeMemoryUnits, 4 )


    def testOverlappingBitRangeRaises( self ) :
        self.testRegister.addBitField( 'field1', [ 0, 5 ] )
        self.assertEqual( len( self.testRegister[ 'bitFields' ] ), 1 )

        with self.assertRaisesRegex( rmr.ConfigurationError, '^Cannot have overlapping bit fields' ) :
            self.testRegister.addBitField( 'field2', [ 5, 6 ] )


class TestRegisterSize( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        # A register with no bit fields must allocate one memory unit for itself.
        self.assertEqual( self.testRegister.sizeMemoryUnits, 1 )


    def testCorrectSizeForBitFieldsAdded( self ) :
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )
        self.assertEqual( self.observer.updateCount, 0 )

        self.testRegister.addBitField( 'f1', [ 0, 7 ] )
        self.assertEqual( self.testRegister.sizeMemoryUnits, 1 )
        # No notifications because the bit range assignment didn't change the register size.
        self.assertEqual( self.observer.updateCount, 0 )
        self.testRegister.addBitField( 'f2', [ 8, 10 ] )

        self.assertEqual( self.testRegister.sizeMemoryUnits, 2 )
        self.assertEqual( self.observer.updateCount, 1 )


    def testCorrectSizeForNonContiguousBitFieldsAdded( self ) :
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )

        self.testRegister.addBitField( 'f1', [ 0, 3 ] )
        self.assertEqual( self.testRegister.sizeMemoryUnits, 1 )
        self.assertEqual( self.observer.updateCount, 0 )
        self.testRegister.addBitField( 'f2', [ 9, 10 ] )

        self.assertEqual( self.testRegister.sizeMemoryUnits, 2 )
        self.assertEqual( self.observer.updateCount, 1 )


    def testFixedSizeExceededAddBitfieldRaises( self ) :
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )

        self.testRegister[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 1
        self.testRegister.addBitField( 'f1', [ 0, 6 ] )
        with self.assertRaisesRegex( rmr.ConstraintError, '^Fixed size exceeded' ) :
            self.testRegister.addBitField( 'f2', [ 8, 10 ] )


    def testChangedBitFieldRangeOverSizeRaises( self ) :
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )
        self.testRegister[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 1
        self.testRegister.addBitField( 'f1', [ 0, 6 ] )

        with self.assertRaisesRegex( rmr.ConstraintError, '^Fixed size exceeded' ) :
            self.testRegister[ 'bitFields' ][ 'f1' ][ 'bitRange' ].value = [ 0, 10 ]


    def testFixedSizeConstraintReportsAsSize( self ) :
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )

        expectedSize = 2
        self.testRegister[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = expectedSize

        self.assertEqual( self.testRegister.sizeMemoryUnits, expectedSize )
        self.assertEqual( self.observer.updateCount, 1 )


class TestRegisterDescription( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = ''
        self.assertEqual( self.testRegister[ 'description' ], expectedValue )


    def testDataAssignmet( self ) :
        expectedValue = 'register description'

        self.assertNotEqual( expectedValue, self.testRegister[ 'description' ] )

        self.testRegister[ 'description' ] = expectedValue

        self.assertEqual( self.testRegister[ 'description' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


class TestRegisterMode( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = 'rw'
        self.assertEqual( self.testRegister[ 'mode' ], expectedValue )


    def testDataAssignment( self ) :
        expectedValue = 'ro'
        self.assertNotEqual( expectedValue, self.testRegister[ 'mode' ] )

        self.testRegister[ 'mode' ] = expectedValue

        self.assertEqual( self.testRegister[ 'mode' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


    def testInvalidValueRaises( self ) :
        with self.assertRaisesRegex( rmr.ConfigurationError, '^Invalid value' ) :
            self.testRegister[ 'mode' ] = 'r'


class TestRegisterName( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testRegister[ 'name' ] )


    def testDataAssignment( self ) :
        expectedValue = 'register name'
        self.assertNotEqual( expectedValue, self.testRegister[ 'name' ] )

        self.testRegister[ 'name' ] = expectedValue

        self.assertEqual( self.testRegister[ 'name' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


class TestRegisterPageRegisterInteraction( unittest.TestCase ) :
    def setUp( self ) :
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.previousRegister = MockPreviousRegister( startAddress = 0,
                                                      sizeMemoryUnits = 4 )
        self.testRegister.previousElement = self.previousRegister


    def testPageSize( self ) :
        self.assertEqual( self.testSpace.addressBits, 32 )
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )

        self.previousRegister.address = 0x278

        log.debug( 'Mock previous register start address: ' + hex( self.previousRegister.address ) )
        log.debug( 'Mock previous register end address: ' + hex( self.previousRegister.endAddress ) )
        self.assertEqual( self.previousRegister.address, 0x278 )
        log.debug( 'Test register start address no page size: ' + hex( self.testRegister.address ) )
        log.debug( 'Test register end address no page size: ' + hex( self.testRegister.endAddress ) )
        self.assertEqual( self.testRegister.address, 0x27c )

        self.testSpace.pageSize = 0x80
        log.debug( 'Test register start address page size '
                   + hex( self.testSpace.pageSize ) + ': '
                   + hex( self.testRegister.address ) )
        log.debug( 'Test register end address page size '
                   + hex( self.testSpace.pageSize ) + ': '
                   + hex( self.testRegister.endAddress ) )
        self.assertEqual( self.testRegister.address, 0x280 )


class TestRegisterPreviousRegister( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testRegister.previousElement )


    def testPreviousRegisterAssign( self ) :
        expectedValue = 0x10
        self.testRegister.previousElement = MockPreviousRegister( startAddress = 0x5,
                                                                  endAddress = (expectedValue - 1) )

        self.assertEqual( self.testRegister.address, expectedValue )


    def testUnassignedPreviousRegisterNoneAddress( self ) :
        fixedAddress = 0x10
        self.testRegister[ 'constraints' ][ 'fixedAddress' ] = fixedAddress

        self.assertEqual( self.testRegister.address, fixedAddress )


    def testUnassignedEndAddress( self ) :
        self.testRegister.previousElement = MockPreviousRegister( )

        actualAddress = self.testRegister.address
        self.assertIsNone( actualAddress )


    def testAssignPreviousRegisterEndAddress( self ) :
        self.testRegister.previousElement = MockPreviousRegister( startAddress = 0x5 )

        self.assertIsNone( self.testRegister.address )

        expectedAddress = 0x10
        self.testRegister.previousElement.endAddress = expectedAddress - 1

        actualAddress = self.testRegister.address
        self.assertEqual( actualAddress, expectedAddress )


class TestRegisterPublic( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = True
        self.assertEqual( self.testRegister[ 'public' ], expectedValue )


    def testDataAssignment( self ) :
        self.assertTrue( self.testRegister[ 'public' ] )

        self.testRegister[ 'public' ] = False

        self.assertFalse( self.testRegister[ 'public' ] )
        self.assertEqual( self.observer.updateCount, 0 )


    def testNonBoolRaises( self ) :
        with self.assertRaisesRegex( rmr.ConfigurationError, '^Public must be specified as boolean' ) :
            self.testRegister[ 'public' ] = 'true'


class TestRegisterSummary( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = ''
        self.assertEqual( self.testRegister[ 'summary' ], expectedValue )


    def testDataAssignment( self ) :
        expectedValue = 'register summary'
        self.assertNotEqual( expectedValue, self.testRegister[ 'summary' ] )

        self.testRegister[ 'summary' ] = expectedValue

        self.assertEqual( self.testRegister[ 'summary' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


class TestRegisterYamlLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.observer = MockObserver( )
        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testEncodeDecode( self ) :
        self.testRegister[ 'constraints' ][ 'fixedAddress' ] = 0x10
        self.testRegister[ 'description' ] = 'some description'
        self.testRegister[ 'mode' ] = 'ro'
        self.testRegister[ 'name' ] = 'registerName'
        self.testRegister[ 'public' ] = False
        self.testRegister[ 'summary' ] = 'a summary'

        self.testRegister.addBitField( 'f1', [ 3, 5 ] )
        self.testRegister.addBitField( 'f2', [ 7, 7 ] )

        encodedYamlData = self.testRegister.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedRegister = rmr.Register.from_yamlData( encodedYamlData, self.testSpace )

        self.assertEqual( decodedRegister[ 'bitFields' ][ 'f1' ][ 'name' ],
                          self.testRegister[ 'bitFields' ][ 'f1' ][ 'name' ] )
        self.assertEqual( decodedRegister[ 'bitFields' ][ 'f1' ][ 'bitRange' ],
                          self.testRegister[ 'bitFields' ][ 'f1' ][ 'bitRange' ] )
        self.assertEqual( decodedRegister[ 'bitFields' ][ 'f2' ][ 'name' ],
                          self.testRegister[ 'bitFields' ][ 'f2' ][ 'name' ] )
        self.assertEqual( decodedRegister[ 'bitFields' ][ 'f2' ][ 'bitRange' ],
                          self.testRegister[ 'bitFields' ][ 'f2' ][ 'bitRange' ] )
        self.assertEqual( decodedRegister[ 'constraints' ][ 'fixedAddress' ],
                          self.testRegister[ 'constraints' ][ 'fixedAddress' ] )
        self.assertEqual( decodedRegister[ 'description' ], self.testRegister[ 'description' ] )
        self.assertEqual( decodedRegister[ 'mode' ], self.testRegister[ 'mode' ] )
        self.assertEqual( decodedRegister[ 'name' ], self.testRegister[ 'name' ] )
        self.assertEqual( decodedRegister[ 'public' ], self.testRegister[ 'public' ] )
        self.assertEqual( decodedRegister[ 'summary' ], self.testRegister[ 'summary' ] )


    def testDefaultEncodeDecode( self ) :
        encodedYamlData = self.testRegister.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedRegister = rmr.Register.from_yamlData( encodedYamlData, self.testSpace )

        self.assertEqual( len( decodedRegister[ 'bitFields' ] ), 0 )
        self.assertEqual( len( decodedRegister[ 'constraints' ] ), 0 )
        self.assertEqual( decodedRegister[ 'description' ], '' )
        self.assertEqual( decodedRegister[ 'mode' ], 'rw' )
        self.assertIsNone( decodedRegister[ 'name' ] )
        self.assertEqual( decodedRegister[ 'public' ], True )
        self.assertEqual( decodedRegister[ 'summary' ], '' )


    def testVadYamlDataRaises( self ) :
        yamlData = { 'mode' : 'ro' }
        with self.assertRaisesRegex( rmr.ConfigurationError, '^Register is not defined in yaml data' ) :
            rmr.Register.from_yamlData( yamlData, self.testSpace,
                                        optional = False )


    def testOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }
        decodedRegister = rmr.Register.from_yamlData( yamlData, self.testSpace,
                                                      optional = True )
        self.assertEqual( len( decodedRegister[ 'bitFields' ] ), 0 )
        self.assertEqual( len( decodedRegister[ 'constraints' ] ), 0 )
        self.assertEqual( decodedRegister[ 'description' ], '' )
        self.assertEqual( decodedRegister[ 'mode' ], 'rw' )
        self.assertIsNone( decodedRegister[ 'name' ] )
        self.assertEqual( decodedRegister[ 'public' ], True )
        self.assertEqual( decodedRegister[ 'summary' ], '' )


class TestRegisterYamlParameters( unittest.TestCase ) :
    def setUp( self ) :
        self.testSpace = rmm.MemorySpace( )
        self.testRegister = rmr.Register( self.testSpace )

        self.previousRegister = MockPreviousRegister( endAddress = 0x3e7,
                                                      sizeMemoryUnits = 4 )
        self.testRegister.previousElement = self.previousRegister

        self.observer = MockObserver( )
        self.testRegister.sizeChangeNotifier.addObserver( self.observer )


    def testYamlDataAddress( self ) :
        # The address data is automatically generated so it is prefixed by '_'.
        self.assertEqual( self.previousRegister.endAddress, 0x3e7 )

        expectedName = '_address'
        expectedValue = 0x3e8

        self.assertEqual( self.testRegister.address, expectedValue )

        yamlData = self.testRegister.to_yamlData( )
        self.assertEqual( yamlData[ 'register' ][ expectedName ], expectedValue )


    def testYamlDataSpan( self ) :
        # The address data is automatically generated so it is prefixed by '_'.
        expectedName = '_sizeMemoryUnits'
        expectedValue = 1

        self.assertEqual( self.testRegister.sizeMemoryUnits, expectedValue )

        yamlData = self.testRegister.to_yamlData( )
        self.assertEqual( yamlData[ 'register' ][ expectedName ], expectedValue )


if __name__ == '__main__' :
    unittest.main( )
