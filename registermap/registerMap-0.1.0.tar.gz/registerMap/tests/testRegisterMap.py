"""
Unit tests for RegisterMap
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

import registerMap.registerMap as rm


log = logging.getLogger( __name__ )


class TestDefaultModuleInstantiation( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = rm.RegisterMap( )


    def testDefaultValues( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )


class TestBaseAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = rm.RegisterMap( )


    def testDefaultBaseAddress( self ) :
        expectedBaseAddress = 0
        actualBaseAddress = self.thisMap.memory.baseAddress

        self.assertTrue( isinstance( actualBaseAddress, int ) )
        self.assertEqual( actualBaseAddress, expectedBaseAddress )


    def testSetBaseAddressGoodValue( self ) :
        expectedBaseAddress = 25

        # Don't test with the default value
        self.assertNotEqual( expectedBaseAddress, self.thisMap.memory.baseAddress )

        self.thisMap.memory.baseAddress = expectedBaseAddress
        actualBaseAddress = self.thisMap.memory.baseAddress

        self.assertEqual( actualBaseAddress, expectedBaseAddress )


class TestMemoryAddress( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = rm.RegisterMap( )


    def testDefaultMemoryAddressBits( self ) :
        expectedMemoryAddressBits = 32
        actualMemoryAddressBits = self.thisMap.memory.addressBits

        self.assertTrue( isinstance( actualMemoryAddressBits, int ) )
        self.assertEqual( actualMemoryAddressBits, expectedMemoryAddressBits )


    def testSetGoodValue( self ) :
        expectedMemoryAddressBits = 20

        self.assertNotEqual( expectedMemoryAddressBits, self.thisMap.memory.addressBits )

        self.thisMap.memory.addressBits = expectedMemoryAddressBits
        actualMemoryAddressBits = self.thisMap.memory.addressBits

        self.assertEqual( actualMemoryAddressBits, expectedMemoryAddressBits )


class TestMemoryUnit( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = rm.RegisterMap( )


    def testDefaultMemoryUnitBits( self ) :
        expectedMemoryUnitBits = 8
        actualMemoryUnitBits = self.thisMap.memory.memoryUnitBits

        self.assertTrue( isinstance( actualMemoryUnitBits, int ) )
        self.assertEqual( actualMemoryUnitBits, expectedMemoryUnitBits )


class TestPageSize( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = rm.RegisterMap( )


    def testDefaultPageSize( self ) :
        actualPageSize = self.thisMap.memory.pageSize

        self.assertIsNone( actualPageSize )


    def testPageSizeAssignment( self ) :
        expectedPageSize = 128

        self.assertNotEqual( expectedPageSize, self.thisMap.memory.pageSize )

        self.thisMap.memory.pageSize = expectedPageSize
        actualPageSize = self.thisMap.memory.pageSize

        self.assertEqual( actualPageSize, expectedPageSize )


class TestRegisterMapModules( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = rm.RegisterMap( )


    def testDefaultModules( self ) :
        self.assertTrue( isinstance( self.thisMap[ 'modules' ], dict ) )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )


class TestAddModule( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = rm.RegisterMap( )


    def testAddSingleModule( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        newModule = self.thisMap.addModule( 'm1' )

        self.assertEqual( self.thisMap.spanMemoryUnits, 0 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertTrue( isinstance( newModule, rm.Module ) )

        self.assertEqual( newModule.baseAddress, self.thisMap.memory.baseAddress )


    def testAddDuplicateModuleNameRaises( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        self.thisMap.addModule( 'm1' )

        with self.assertRaisesRegex( rm.ConfigurationError,
                                     '^Created module names must be unique within a register map' ) :
            self.thisMap.addModule( 'm1' )


class TestModuleAddresses( unittest.TestCase ) :
    def setUp( self ) :
        self.thisMap = rm.RegisterMap( )


    def testBaseAddressUpdate( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        m1 = self.thisMap.addModule( 'm1' )
        self.assertEqual( self.thisMap.spanMemoryUnits, 0 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertEqual( m1.baseAddress, self.thisMap.memory.baseAddress )

        r1 = m1.addRegister( 'r1' )
        self.assertEqual( self.thisMap.spanMemoryUnits, 1 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 1 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertEqual( r1.address, self.thisMap.memory.baseAddress )

        self.thisMap.memory.baseAddress = 0x10

        # Existing register and module must reflect the base address change.
        self.assertEqual( m1.baseAddress, self.thisMap.memory.baseAddress )
        self.assertEqual( r1.address, self.thisMap.memory.baseAddress )


    def testModuleSequentialAddresses( self ) :
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        m1 = self.thisMap.addModule( 'm1' )
        self.assertEqual( self.thisMap.spanMemoryUnits, 0 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertEqual( m1.baseAddress, self.thisMap.memory.baseAddress )

        r1 = m1.addRegister( 'r1' )
        self.assertEqual( self.thisMap.spanMemoryUnits, 1 )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 1 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 1 )
        self.assertEqual( r1.address, self.thisMap.memory.baseAddress )

        m2 = self.thisMap.addModule( 'm2' )
        r2 = m2.addRegister( 'r2' )

        self.thisMap.memory.baseAddress = 0x10

        # Existing registers and modules must reflect the base address change.
        self.assertEqual( m1.baseAddress, self.thisMap.memory.baseAddress )
        self.assertEqual( r1.address, self.thisMap.memory.baseAddress )
        self.assertEqual( m2.baseAddress, (self.thisMap.memory.baseAddress + 1) )
        self.assertEqual( r2.address, (self.thisMap.memory.baseAddress + 1) )


    def testAssignedCount( self ) :
        self.assertEqual( self.thisMap.memory.memoryUnitBits, 8 )
        self.assertIsNone( self.thisMap.spanMemoryUnits )
        self.assertEqual( self.thisMap.assignedMemoryUnits, 0 )
        self.assertEqual( len( self.thisMap[ 'modules' ] ), 0 )

        m1 = self.thisMap.addModule( 'm1' )
        r1 = m1.addRegister( 'r1' )
        m2 = self.thisMap.addModule( 'm2' )
        r2 = m2.addRegister( 'r2' )
        r2.addBitField( 'f2', [ 3, 10 ] )
        r2[ 'constraints' ][ 'fixedAddress' ] = 0x15

        log.debug( 'm1 address before base assigment: ' + hex( m1.baseAddress ) )
        log.debug( 'm2 address before base assigment: ' + hex( m2.baseAddress ) )
        log.debug( 'r1 address before base assigment: ' + hex( r1.address ) )
        log.debug( 'r2 address before base assigment: ' + hex( r2.address ) )

        self.assertEqual( self.thisMap.assignedMemoryUnits, 3 )
        self.assertEqual( self.thisMap.spanMemoryUnits, 22 )

        log.debug( 'register map base address assignment' )
        self.thisMap.memory.baseAddress = 0x10

        log.debug( 'm1 address after base assigment: ' + hex( m1.baseAddress ) )
        log.debug( 'm2 address after base assigment: ' + hex( m2.baseAddress ) )
        log.debug( 'r1 address after base assigment: ' + hex( r1.address ) )
        log.debug( 'r2 address after base assigment: ' + hex( r2.address ) )

        self.assertEqual( m1.spanMemoryUnits, 1 )
        self.assertEqual( m2.spanMemoryUnits, 6 )

        self.assertEqual( self.thisMap.assignedMemoryUnits, 3 )
        self.assertEqual( self.thisMap.spanMemoryUnits, 6 )


class TestYamlLoadSave( unittest.TestCase ) :
    def testEncodeDecode( self ) :
        m = rm.RegisterMap( )

        m.memory.addressBits = 48
        m.memory.baseAddress = 0x1000
        m.memory.memoryUnitBits = 16
        m.memory.pageSize = 128
        m[ 'description' ] = 'some description'
        m[ 'summary' ] = 'a summary'
        self.createSampleModule( m, 'm1' )

        encodedYamlData = m.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedMap = rm.RegisterMap.from_yamlData( encodedYamlData )

        self.assertEqual( decodedMap.memory.addressBits, m.memory.addressBits )
        self.assertEqual( decodedMap.memory.baseAddress, m.memory.baseAddress )
        self.assertEqual( decodedMap.memory.memoryUnitBits, m.memory.memoryUnitBits )
        self.assertEqual( decodedMap.memory.pageSize, m.memory.pageSize )
        self.assertEqual( decodedMap[ 'description' ], m[ 'description' ] )
        self.assertEqual( decodedMap[ 'summary' ], m[ 'summary' ] )

        self.assertEqual( len( decodedMap[ 'modules' ] ), len( m[ 'modules' ] ) )
        self.assertEqual( decodedMap[ 'modules' ][ 'm1' ][ 'name' ], 'm1' )


    def createSampleModule( self, thisMap, moduleName ) :
        sampleModule = thisMap.addModule( moduleName )

        registerName = 'r1'
        sampleModule.addRegister( registerName )

        sampleModule[ 'registers' ][ registerName ][ 'constraints' ][ 'fixedAddress' ] = 0x1010
        sampleModule[ 'registers' ][ registerName ][ 'description' ] = 'some description'
        sampleModule[ 'registers' ][ registerName ][ 'mode' ] = 'ro'
        sampleModule[ 'registers' ][ registerName ][ 'public' ] = False
        sampleModule[ 'registers' ][ registerName ][ 'summary' ] = 'a summary'

        sampleModule[ 'registers' ][ registerName ].addBitField( 'f1', [ 3, 5 ] )
        sampleModule[ 'registers' ][ registerName ].addBitField( 'f2', [ 7, 7 ] )


    def testFromBadYamlDataRaises( self ) :
        yamlData = { 'mode' : 'ro' }

        with self.assertRaisesRegex( rm.ParseError, '^RegisterMap is not defined in yaml data' ) :
            rm.RegisterMap.from_yamlData( yamlData,
                                          optional = False )


    def testOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }

        m = rm.RegisterMap.from_yamlData( yamlData,
                                          optional = True )

        self.assertEqual( m.memory.addressBits, 32 )
        self.assertEqual( m.memory.baseAddress, 0 )
        self.assertEqual( m.memory.memoryUnitBits, 8 )
        self.assertIsNone( m.memory.pageSize )
        self.assertEqual( len( m[ 'modules' ] ), 0 )


    def testSynchronization( self ) :
        thisMap = rm.RegisterMap( )

        thisMap.memory.addressBits = 48
        thisMap.memory.baseAddress = 0
        thisMap.memory.memoryUnitBits = 8
        thisMap.memory.pageSize = None

        m1 = thisMap.addModule( 'm1' )
        r1 = m1.addRegister( 'r1' )
        m2 = thisMap.addModule( 'm2' )
        r2 = m2.addRegister( 'r2' )
        r2.addBitField( 'f2', [ 3, 10 ] )
        r2[ 'constraints' ][ 'fixedAddress' ] = 0x15

        encodedYamlData = thisMap.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedMap = rm.RegisterMap.from_yamlData( encodedYamlData )

        # Changing the base address for each map must mean that elements end up with the same addresses.
        thisMap.memory.baseAddress = 0x10
        decodedMap.memory.baseAddress = 0x10

        # Existing registers and modules must reflect the base address change.
        self.assertEqual( decodedMap[ 'modules' ][ 'm1' ].baseAddress, m1.baseAddress )
        self.assertEqual( decodedMap[ 'modules' ][ 'm1' ][ 'registers' ][ 'r1' ].address, r1.address )
        self.assertEqual( decodedMap[ 'modules' ][ 'm2' ].baseAddress, m2.baseAddress )
        self.assertEqual( decodedMap[ 'modules' ][ 'm2' ][ 'registers' ][ 'r2' ].address, r2.address )

        if __name__ == '__main__' :
            unittest.main( )
