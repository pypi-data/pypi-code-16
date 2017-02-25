"""
Test BitField.
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

import registerMap.elements.bitRange as rmbr
import registerMap.elements.bitfield as rmf
from registerMap.elements.tests.mockObserver import MockObserver


log = logging.getLogger( __name__ )


class TestFieldBitRange( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testField = rmf.BitField( )

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertIsNone( self.testField[ 'bitRange' ].value )


    def testDataAssignment( self ) :
        expectedValue = rmbr.BitRange( value = [ 4, 7 ] )
        self.assertNotEqual( expectedValue, self.testField[ 'bitRange' ] )

        self.testField[ 'bitRange' ] = expectedValue
        actualValue = self.testField[ 'bitRange' ]

        self.assertEqual( actualValue, expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )


    def testChangedValueNotifies( self ) :
        expectedValue = [ 4, 7 ]
        self.assertNotEqual( self.testField[ 'bitRange' ], expectedValue )

        self.testField[ 'bitRange' ].value = expectedValue

        self.assertEqual( self.observer.updateCount, 1 )


class TestFieldDescription( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testField = rmf.BitField( )

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = ''
        self.assertEqual( self.testField[ 'description' ], expectedValue )


    def testDataAssignment( self ) :
        expectedValue = 'some description'
        self.assertNotEqual( expectedValue, self.testField[ 'description' ] )

        self.testField[ 'description' ] = expectedValue

        self.assertEqual( self.testField[ 'description' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


class TestFieldName( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testField = rmf.BitField( )

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = 'unassigned'
        self.assertEqual( self.testField[ 'name' ], expectedValue )


    def testDataAssignment( self ) :
        expectedValue = 'new name'
        self.assertNotEqual( expectedValue, self.testField[ 'name' ] )

        self.testField[ 'name' ] = expectedValue

        self.assertEqual( self.testField[ 'name' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


class TestFieldPublic( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testField = rmf.BitField( )

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = True
        self.assertEqual( self.testField[ 'public' ], expectedValue )


    def testDataAssignment( self ) :
        self.assertTrue( self.testField[ 'public' ] )

        self.testField[ 'public' ] = False

        self.assertFalse( self.testField[ 'public' ] )
        self.assertEqual( self.observer.updateCount, 0 )


    def testNonBoolRaises( self ) :
        with self.assertRaisesRegex( rmf.ConfigurationError, '^Public must be specified as boolean' ) :
            self.testField[ 'public' ] = 'true'


class TestFieldResetValue( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testField = rmf.BitField( )

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        self.assertEqual( self.testField[ 'resetValue' ], 0 )


    def testDataAssignment( self ) :
        expectedValue = 0xd
        self.testField[ 'bitRange' ] = rmbr.BitRange( value = [ 0, 8 ] )
        self.assertEqual( self.observer.updateCount, 1 )
        self.assertNotEqual( expectedValue, self.testField[ 'resetValue' ] )

        self.testField[ 'resetValue' ] = expectedValue
        actualValue = self.testField[ 'resetValue' ]

        self.assertEqual( actualValue, expectedValue )
        self.assertEqual( self.observer.updateCount, 1 )


    def testNonIntRaises( self ) :
        with self.assertRaisesRegex( rmf.ConfigurationError,
                                     '^Reset value must be specified as non-negative integer' ) :
            self.testField[ 'resetValue' ] = '5'


    def testNegativeIntRaises( self ) :
        with self.assertRaisesRegex( rmf.ConfigurationError,
                                     '^Reset value must be specified as non-negative integer' ) :
            self.testField[ 'resetValue' ] = -5


    def testResetValueGreaterThanBitRangeRaises( self ) :
        self.testField[ 'bitRange' ] = rmbr.BitRange( value = [ 5, 6 ] )
        with self.assertRaisesRegex( rmf.ConfigurationError,
                                     '^Reset value cannot exceed number of bits of field' ) :
            self.testField[ 'resetValue' ] = 8


    def testResetValueAssignBitRangeUndefinedRaises( self ) :
        self.assertIsNone( self.testField[ 'bitRange' ].value )
        with self.assertRaisesRegex( rmf.ConfigurationError, '^Bit range not defined' ) :
            self.testField[ 'resetValue' ] = 8


class TestFieldSummary( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testField = rmf.BitField( )

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testDefaultValue( self ) :
        expectedValue = ''
        self.assertEqual( self.testField[ 'summary' ], expectedValue )


    def testDataAssignment( self ) :
        expectedValue = 'does something'
        self.assertNotEqual( expectedValue, self.testField[ 'summary' ] )

        self.testField[ 'summary' ] = expectedValue

        self.assertEqual( self.testField[ 'summary' ], expectedValue )
        self.assertEqual( self.observer.updateCount, 0 )


class TestLoadSave( unittest.TestCase ) :
    def setUp( self ) :
        self.observer = MockObserver( )
        self.testField = rmf.BitField( )

        self.testField.sizeChangeNotifier.addObserver( self.observer )


    def testEncodeDecode( self ) :
        self.testField[ 'bitRange' ].value = [ 0, 7 ]
        self.testField[ 'description' ] = 'some description'
        self.testField[ 'name' ] = 'f1'
        self.testField[ 'public' ] = False
        self.testField[ 'resetValue' ] = 0x5a
        self.testField[ 'summary' ] = 'a summary'

        encodedYamlData = self.testField.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = rmf.BitField.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData[ 'bitRange' ], self.testField[ 'bitRange' ] )
        self.assertEqual( decodedData[ 'description' ], self.testField[ 'description' ] )
        self.assertEqual( decodedData[ 'name' ], self.testField[ 'name' ] )
        self.assertEqual( decodedData[ 'public' ], self.testField[ 'public' ] )
        self.assertEqual( decodedData[ 'resetValue' ], self.testField[ 'resetValue' ] )
        self.assertEqual( decodedData[ 'summary' ], self.testField[ 'summary' ] )


    def testOptionalDescription( self ) :
        self.testField[ 'bitRange' ].value = [ 0, 7 ]
        self.testField[ 'name' ] = 'f1'
        self.testField[ 'public' ] = False
        self.testField[ 'resetValue' ] = 0x5a
        self.testField[ 'summary' ] = 'a summary'

        encodedYamlData = self.testField.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = rmf.BitField.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData[ 'description' ], '' )


    def testOptionalSummary( self ) :
        self.testField[ 'bitRange' ].value = [ 0, 7 ]
        self.testField[ 'description' ] = 'some description'
        self.testField[ 'name' ] = 'f1'
        self.testField[ 'public' ] = False
        self.testField[ 'resetValue' ] = 0x5a

        encodedYamlData = self.testField.to_yamlData( )
        log.debug( 'Encoded yaml data: ' + repr( encodedYamlData ) )
        decodedData = rmf.BitField.from_yamlData( encodedYamlData )

        self.assertEqual( decodedData[ 'bitRange' ], self.testField[ 'bitRange' ] )
        self.assertEqual( decodedData[ 'description' ], self.testField[ 'description' ] )
        self.assertEqual( decodedData[ 'name' ], self.testField[ 'name' ] )
        self.assertEqual( decodedData[ 'public' ], self.testField[ 'public' ] )
        self.assertEqual( decodedData[ 'resetValue' ], self.testField[ 'resetValue' ] )
        self.assertEqual( decodedData[ 'summary' ], '' )


if __name__ == '__main__' :
    unittest.main( )
