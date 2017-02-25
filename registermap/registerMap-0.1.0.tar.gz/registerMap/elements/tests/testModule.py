"""
Unit test Module class
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

import logging
import unittest

import registerMap.elements.memory as rmm
import registerMap.elements.module as rmd
import registerMap.elements.register as rmr
import registerMap.exceptions as rmx
import registerMap.utility.observer as rmo

from registerMap.elements.tests.mockObserver import MockObserver


log = logging.getLogger( __name__ )


class MockPreviousModule :
    def __init__( self,
                  endAddress = None ) :
        self.addressChangeNotifier = rmo.Observable( )
        self.sizeChangeNotifier = rmo.Observable( )

        self.__endAddress = endAddress


    @property
    def endAddress( self ) :
        return self.__endAddress


    @endAddress.setter
    def endAddress( self, value ) :
        self.__endAddress = value
        self.sizeChangeNotifier.notifyObservers( )


class TestFirstRegister( unittest.TestCase ) :
    def setUp( self ) :
        pass


    def testGetEndAddressProperty( self ) :
        expectedValue = 0x10
        firstRegister = rmd.RegistersParameter.FirstRegister( endAddress = expectedValue )
        self.assertEqual( firstRegister.endAddress, expectedValue )


    def testSetEndAddressProperty( self ) :
        expectedValue = 0x10
        firstRegister = rmd.RegistersParameter.FirstRegister( endAddress = 0x20 )
        self.assertNotEqual( firstRegister.endAddress, expectedValue )

        firstRegister.endAddress = expectedValue

        self.assertEqual( firstRegister.endAddress, expectedValue )


class TestModule( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultMemory( self ) :
        self.assertEqual( self.testModule.memory.memoryUnitBits, 8 )

        self.assertIsNone( self.testModule.baseAddress )
        self.assertIsNone( self.testModule.previousElement )
        self.assertIsNone( self.testModule.spanMemoryUnits )
        self.assertEqual( self.testModule.assignedMemoryUnits, 0 )


    def testAddSingleRegister( self ) :
        self.assertEqual( self.testModule.memory.memoryUnitBits, 8 )

        self.testModule.addRegister( 'r1' )

        self.assertIsNone( self.testModule.baseAddress )
        self.assertIsNone( self.testModule.previousElement )
        self.assertIsNone( self.testModule.spanMemoryUnits )
        self.assertEqual( self.testModule.assignedMemoryUnits, 1 )


    def testReviewAddressChangeEmptyModule( self ) :
        testModule = rmd.Module( self.testSpace )

        self.assertEqual( len( testModule[ 'registers' ] ), 0 )

        # No exceptions should be thrown
        testModule.reviewAddressChange( )

        self.assertIsNone( testModule.baseAddress )


    def testReviewAddressChangeEmptyModuleFromYaml( self ) :
        testModule = rmd.Module( self.testSpace )

        self.assertEqual( len( testModule[ 'registers' ] ), 0 )

        yamlData = testModule.to_yamlData( )
        generatedModule = rmd.Module.from_yamlData( yamlData, self.testSpace )

        # No exceptions should be thrown
        generatedModule.reviewAddressChange( )

        self.assertIsNone( generatedModule.baseAddress )


class TestModuleWithPreviousModule( unittest.TestCase ) :
    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x10 )
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultMemory( self ) :
        self.assertEqual( self.testModule.memory.memoryUnitBits, 8 )

        self.assertEqual( self.testModule.baseAddress, (self.previousModule.endAddress + 1) )
        self.assertEqual( self.testModule.spanMemoryUnits, 0 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 0 )


    def testAddSingleRegister( self ) :
        self.assertEqual( self.testModule.memory.memoryUnitBits, 8 )

        self.testModule.addRegister( 'r1' )

        self.assertEqual( self.testModule.baseAddress, (self.previousModule.endAddress + 1) )
        self.assertEqual( self.testModule.spanMemoryUnits, 1 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 1 )


class TestModuleAddRegisterNoneAddresses( unittest.TestCase ) :
    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = None )
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testAddSingleRegister( self ) :
        expectedName = 'r1'

        self.assertEqual( len( self.testModule[ 'registers' ] ), 0 )

        addedRegister = self.testModule.addRegister( expectedName )

        self.assertEqual( len( self.testModule[ 'registers' ] ), 1 )
        self.assertEqual( self.testModule[ 'registers' ][ expectedName ][ 'name' ], expectedName )
        # The addRegister method returns the created register
        self.assertEqual( addedRegister, self.testModule[ 'registers' ][ expectedName ] )

        self.assertIsNone( addedRegister.address )


    def testAddDuplicateRegisterRaises( self ) :
        # A register name is unique to its module
        expectedName = 'r1'
        self.testModule.addRegister( expectedName )
        with self.assertRaisesRegex( rmd.ConfigurationError,
                                     '^Created register names must be unique within a module' ) :
            self.testModule.addRegister( expectedName )


    def testAddMultipleRegistersWithSubsequentConcreteAddress( self ) :
        r1 = self.testModule.addRegister( 'r1' )
        self.assertIsNone( r1.address )
        r2 = self.testModule.addRegister( 'r2' )
        self.assertIsNone( r2.address )

        previousModule = MockPreviousModule( endAddress = 0x10 )

        self.testModule.previousElement = previousModule

        self.assertEqual( self.testModule.baseAddress, 0x11 )
        self.assertEqual( r1.address, 0x11 )
        self.assertEqual( r2.address, 0x12 )


class TestModuleAddRegisterConcreteAddresses( unittest.TestCase ) :
    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x10 )
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testAddSingleRegister( self ) :
        expectedName = 'r1'

        self.assertEqual( len( self.testModule[ 'registers' ] ), 0 )

        addedRegister = self.testModule.addRegister( expectedName )

        self.assertEqual( len( self.testModule[ 'registers' ] ), 1 )
        self.assertEqual( self.testModule[ 'registers' ][ expectedName ][ 'name' ], expectedName )
        # The addRegister method returns the created register
        self.assertEqual( addedRegister, self.testModule[ 'registers' ][ expectedName ] )

        self.assertEqual( addedRegister.address, self.testModule.baseAddress )


class TestModuleConstraints( unittest.TestCase ) :
    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x10 )
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testFixedAddress( self ) :
        expectedValue = 0x15

        self.assertGreater( expectedValue, self.previousModule.endAddress )
        self.assertNotEqual( self.testModule.baseAddress, expectedValue )

        self.testModule[ 'constraints' ][ 'fixedAddress' ] = expectedValue

        self.assertEqual( self.testModule.baseAddress, expectedValue )


    def testAlignedAddress( self ) :
        alignmentValue = 2
        expectedValue = self.previousModule.endAddress + 2

        self.assertEqual( (expectedValue % alignmentValue), 0 )
        self.assertLess( self.testModule.baseAddress, expectedValue )

        self.assertNotEqual( self.testModule.baseAddress, expectedValue )

        self.testModule[ 'constraints' ][ 'alignmentMemoryUnits' ] = alignmentValue

        self.assertEqual( self.testModule.baseAddress, expectedValue )


    def testAddRegisterOverFixedSizeRaises( self ) :
        self.assertEqual( self.testModule.spanMemoryUnits, 0 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 0 )
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )

        self.testModule[ 'constraints' ][ 'fixedSizeMemoryUnits' ] = 3

        r1 = self.testModule.addRegister( 'r1' )
        r1.addBitField( 'f1', [ 0, 10 ] )
        self.testModule.addRegister( 'r2' )

        self.assertEqual( self.testModule.spanMemoryUnits, 3 )

        with self.assertRaisesRegex( rmx.ConstraintError, '^Fixed size exceeded' ) :
            # A register has a size of one memory unit even if it has no bit fields.
            # So adding a third register must exceed the size limit
            self.testModule.addRegister( 'r3' )


class TestModuleDescription( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertEqual( self.testModule[ 'description' ], '' )


class TestModuleName( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testModule[ 'name' ] )


class TestModulePageRegisterInteraction( unittest.TestCase ) :
    def setUp( self ) :
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.previousModule = MockPreviousModule( endAddress = 0 )
        self.testModule.previousElement = self.previousModule


    def testModuleOnPageRegister( self ) :
        self.assertEqual( self.testSpace.addressBits, 32 )
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )

        self.previousModule.endAddress = 0x27b

        log.debug( 'Mock previous module end address: ' + hex( self.previousModule.endAddress ) )
        self.assertEqual( self.previousModule.endAddress, 0x27b )
        log.debug( 'Test module start address no page size: ' + hex( self.testModule.baseAddress ) )
        log.debug( 'Test module end address no page size: ' + hex( self.testModule.endAddress ) )
        self.assertEqual( self.testModule.baseAddress, 0x27c )

        self.testSpace.pageSize = 0x80
        log.debug( 'Test module start address page size '
                   + hex( self.testSpace.pageSize ) + ': '
                   + hex( self.testModule.baseAddress ) )
        log.debug( 'Test module end address page size '
                   + hex( self.testSpace.pageSize ) + ': '
                   + hex( self.testModule.endAddress ) )
        self.assertEqual( self.testModule.baseAddress, 0x280 )


class TestModulePreviousModule( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testModule.previousElement )


    def testAssignPreviousModuleNoneEndAddress( self ) :
        previousModule = MockPreviousModule( )
        self.testModule.previousElement = previousModule

        self.assertIsNone( self.testModule.endAddress )


    def testUpdatePreviousModuleEndAddress( self ) :
        previousModule = MockPreviousModule( )
        self.testModule.previousElement = previousModule

        expectedAddress = 0x10
        previousModule.endAddress = expectedAddress - 1

        self.assertEqual( self.testModule.baseAddress, expectedAddress )


class TestModuleSizePreviousConcreteAddresses( unittest.TestCase ) :
    # Module size is the number of memory units spanned by registers from the lowest memory unit to the highest memory unit.
    # - If a module has a fixed address then the lowest memory unit is always the fixed address.
    # - If a page size is specified, then register addresses must miss paging registers (a fixed address on a page register must raise).
    def setUp( self ) :
        self.observer = MockObserver( )
        self.previousModule = MockPreviousModule( endAddress = 0x10 )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertEqual( self.testModule.spanMemoryUnits, 0 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 0 )


    def testContiguousRegisters( self ) :
        self.assertEqual( self.testModule.spanMemoryUnits, 0 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 0 )
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )

        r1 = self.testModule.addRegister( 'r1' )
        r1.addBitField( 'f1', [ 0, 10 ] )
        self.assertEqual( self.testModule.spanMemoryUnits, 2 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 2 )

        r2 = self.testModule.addRegister( 'r2' )

        self.assertEqual( self.testModule.spanMemoryUnits, 3 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 3 )


    def testDiscontiguousRegisters( self ) :
        self.assertEqual( self.testModule.spanMemoryUnits, 0 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 0 )
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )
        self.assertEqual( self.testModule.baseAddress, (self.previousModule.endAddress + 1) )

        r1 = self.testModule.addRegister( 'r1' )
        r1.addBitField( 'f1', [ 0, 10 ] )
        self.assertEqual( self.testModule.spanMemoryUnits, 2 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 2 )

        r2 = self.testModule.addRegister( 'r2' )
        self.assertEqual( r2.sizeMemoryUnits, 1 )
        self.assertEqual( self.testModule.spanMemoryUnits, 3 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 3 )

        expectedAddress = 0x15
        r2[ 'constraints' ][ 'fixedAddress' ] = expectedAddress

        self.assertEqual( r2.address, expectedAddress )
        self.assertEqual( self.testModule.spanMemoryUnits, (expectedAddress - self.testModule.baseAddress + 1) )
        self.assertEqual( self.testModule.assignedMemoryUnits, 3 )


    def testDiscontiguousRegistersWithMultiunitRegister( self ) :
        self.assertEqual( self.testModule.spanMemoryUnits, 0 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 0 )
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )
        self.assertEqual( self.testModule.baseAddress, (self.previousModule.endAddress + 1) )

        r1 = self.testModule.addRegister( 'r1' )
        self.assertEqual( self.testModule.spanMemoryUnits, 1 )

        r2 = self.testModule.addRegister( 'r2' )
        r2.addBitField( 'f1', [ 0, 10 ] )
        self.assertEqual( r2.sizeMemoryUnits, 2 )
        self.assertEqual( self.testModule.spanMemoryUnits, 3 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 3 )

        expectedAddress = 0x15
        r2[ 'constraints' ][ 'fixedAddress' ] = expectedAddress

        self.assertEqual( r2.address, expectedAddress )
        self.assertEqual( self.testModule.spanMemoryUnits, 6 )
        self.assertEqual( self.testModule.assignedMemoryUnits, 3 )


class TestModuleSizePreviousNoneAddresses( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.previousModule = MockPreviousModule( endAddress = None )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testDiscontiguousRegisters( self ) :
        self.assertIsNone( self.testModule.spanMemoryUnits )
        self.assertEqual( self.testModule.assignedMemoryUnits, 0 )
        self.assertEqual( self.testSpace.memoryUnitBits, 8 )
        self.assertIsNone( self.testModule.baseAddress )

        r1 = self.testModule.addRegister( 'r1' )
        r1.addBitField( 'f1', [ 0, 10 ] )
        self.assertIsNone( self.testModule.spanMemoryUnits )
        self.assertEqual( self.testModule.assignedMemoryUnits, 2 )

        r2 = self.testModule.addRegister( 'r2' )
        self.assertEqual( r2.sizeMemoryUnits, 1 )
        self.assertIsNone( self.testModule.spanMemoryUnits )
        self.assertEqual( self.testModule.assignedMemoryUnits, 3 )

        expectedAddress = 0x15
        r2[ 'constraints' ][ 'fixedAddress' ] = expectedAddress

        self.assertEqual( r2.address, expectedAddress )
        self.assertIsNone( self.testModule.spanMemoryUnits )
        self.assertEqual( self.testModule.assignedMemoryUnits, 3 )


class TestModuleSpanPreviousAddressChange( unittest.TestCase ) :
    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x0 )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule

        self.observer = MockObserver( )
        self.testModule.sizeChangeNotifier.addObserver( self.observer )
        self.testModule.addressChangeNotifier.addObserver( self.observer )


    def testSpanAfterPreviousAddressChange( self ) :
        r1 = self.testModule.addRegister( 'r1' )
        r1[ 'constraints' ][ 'fixedAddress' ] = 0x15

        self.previousModule.endAddress = 0x10
        # Because of the fixedAddress constraint on the register, the module span is implicitly a function of the
        # base address and the fixed address constraint.
        self.assertEqual( self.testModule.baseAddress, 0x11 )
        self.assertEqual( self.testModule.spanMemoryUnits, 5 )


class TestModuleYamlLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.previousModule = MockPreviousModule( endAddress = 0x0 )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule

        self.testModule.sizeChangeNotifier.addObserver( self.observer )


    def testEncodeDecode( self ) :
        self.testModule[ 'constraints' ][ 'fixedAddress' ] = 0x10
        self.createRegister( 'r1' )

        encodedYamlData = self.testModule.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedModule = rmd.Module.from_yamlData( encodedYamlData, self.testSpace )

        self.assertEqual( decodedModule[ 'constraints' ][ 'fixedAddress' ],
                          self.testModule[ 'constraints' ][ 'fixedAddress' ] )
        self.assertEqual( decodedModule[ 'description' ], self.testModule[ 'description' ] )
        self.assertEqual( decodedModule[ 'summary' ], self.testModule[ 'summary' ] )

        decodedModule.previousElement = self.previousModule
        # No exceptions should be thrown
        decodedModule.reviewAddressChange( )


    def createRegister( self, name ) :
        self.testModule.addRegister( name )

        self.testModule[ 'registers' ][ name ][ 'constraints' ][ 'fixedAddress' ] = 0x10
        self.testModule[ 'registers' ][ name ][ 'description' ] = 'some description'
        self.testModule[ 'registers' ][ name ][ 'mode' ] = 'ro'
        self.testModule[ 'registers' ][ name ][ 'public' ] = False
        self.testModule[ 'registers' ][ name ][ 'summary' ] = 'a summary'

        self.testModule[ 'registers' ][ name ].addBitField( 'f1', [ 3, 5 ] )
        self.testModule[ 'registers' ][ name ].addBitField( 'f2', [ 7, 7 ] )


    def testFromBadYamlData( self ) :
        yamlData = { 'mode' : 'ro' }

        with self.assertRaisesRegex( rmd.ParseError, '^Module is not defined in yaml data' ) :
            rmd.Module.from_yamlData( yamlData, self.testSpace )


    def testFromOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }

        decodedModule = rmd.Module.from_yamlData( yamlData, self.testSpace,
                                                  optional = True )

        self.assertEqual( len( decodedModule[ 'constraints' ] ), 0 )
        self.assertEqual( decodedModule[ 'description' ], '' )
        self.assertIsNone( decodedModule[ 'name' ] )
        self.assertEqual( len( decodedModule[ 'registers' ] ), 0 )
        self.assertEqual( decodedModule[ 'summary' ], '' )


class TestModuleYamlParameters( unittest.TestCase ) :
    def setUp( self ) :
        self.previousModule = MockPreviousModule( endAddress = 0x215 )
        self.testSpace = rmm.MemorySpace( )
        self.testModule = rmd.Module( self.testSpace )

        self.testModule.previousElement = self.previousModule


    def testYamlDataAddress( self ) :
        # The address data is automatically generated so it is prefixed by '_'.
        self.assertEqual( self.previousModule.endAddress, 0x215 )

        expectedName = '_address'
        expectedValue = 0x216

        self.assertEqual( self.testModule.baseAddress, expectedValue )

        yamlData = self.testModule.to_yamlData( )
        self.assertEqual( yamlData[ 'module' ][ expectedName ], expectedValue )


    def testYamlDataSpan( self ) :
        # The address data is automatically generated so it is prefixed by '_'.
        expectedName = '_spanMemoryUnits'
        expectedValue = 0

        self.assertEqual( self.testModule.spanMemoryUnits, expectedValue )

        yamlData = self.testModule.to_yamlData( )
        self.assertEqual( yamlData[ 'module' ][ expectedName ], expectedValue )


    def testYamlDataNoneAddress( self ) :
        testModule = rmd.Module( self.testSpace )

        yamlData = testModule.to_yamlData( )
        self.assertIsNone( yamlData[ 'module' ][ '_address' ] )


if __name__ == '__main__' :
    unittest.main( )
