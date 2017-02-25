#
# Copyright 2017 Russell Smiley
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

import unittest

import registerMap.elements.module as rmd


class TestModuleRegistersParameter( unittest.TestCase ) :
    def setUp( self ) :
        self.memorySpace = rmd.MemorySpace( )
        self.module = rmd.Module( self.memorySpace )


    def testInitialization( self ) :
        p = rmd.RegistersParameter( self.module )

        self.assertEqual( p.name, 'registers' )
        self.assertTrue( isinstance( p.value, rmd.rml.ElementList ) )


    def testEmptyBitFieldsToYamlData( self ) :
        p = rmd.RegistersParameter( self.module )

        expectedYamlData = { 'registers' : list( ) }
        actualYamlData = p.to_yamlData( )

        self.assertEqual( actualYamlData, expectedYamlData )


    def testSingleRegisterToYamlData( self ) :
        p = rmd.RegistersParameter( self.module )
        p.value[ 'r1' ] = self.createRegister( 'r1' )

        expectedYamlData = { 'registers' : [
            p.value[ 'r1' ].to_yamlData( )
        ] }
        actualYamlData = p.to_yamlData( )

        self.assertEqual( actualYamlData, expectedYamlData )


    def testMultipleRegistersToYamlData( self ) :
        p = rmd.RegistersParameter( self.module )
        p.value[ 'r1' ] = self.createRegister( 'r1' )
        p.value[ 'r2' ] = self.createRegister( 'r2', 0x12 )

        expectedYamlData = { 'registers' : [
            p.value[ 'r1' ].to_yamlData( ),
            p.value[ 'r2' ].to_yamlData( )
        ] }
        actualYamlData = p.to_yamlData( )

        self.assertEqual( actualYamlData, expectedYamlData )


    def createRegister( self, name,
                        fixedAddress = 0x10 ) :
        register = rmd.rmr.Register( self.memorySpace )
        register[ 'constraints' ][ 'fixedAddress' ] = fixedAddress
        register[ 'description' ] = 'some description'
        register[ 'mode' ] = 'ro'
        register[ 'name' ] = name
        register[ 'public' ] = False
        register[ 'summary' ] = 'a summary'

        register.addBitField( 'f1', [ 3, 5 ] )
        register.addBitField( 'f2', [ 7, 7 ] )

        return register


    def testFromGoodYamlData( self ) :
        p = rmd.RegistersParameter( self.module )
        p.value[ 'r1' ] = self.createRegister( 'r1' )
        p.value[ 'r2' ] = self.createRegister( 'r2', 0x12 )

        yamlData = p.to_yamlData( )
        gp = rmd.RegistersParameter.from_yamlData( yamlData, self.module, self.memorySpace )

        self.assertEqual( gp.value[ 'r1' ][ 'bitFields' ][ 'f1' ][ 'name' ], 'f1' )
        self.assertEqual( gp.value[ 'r1' ][ 'bitFields' ][ 'f1' ][ 'bitRange' ].value, [ 3, 5 ] )
        self.assertEqual( gp.value[ 'r1' ][ 'bitFields' ][ 'f2' ][ 'name' ], 'f2' )
        self.assertEqual( gp.value[ 'r1' ][ 'bitFields' ][ 'f2' ][ 'bitRange' ].value, [ 7, 7 ] )

        self.assertEqual( gp.value[ 'r2' ][ 'bitFields' ][ 'f1' ][ 'name' ], 'f1' )
        self.assertEqual( gp.value[ 'r2' ][ 'bitFields' ][ 'f1' ][ 'bitRange' ].value, [ 3, 5 ] )
        self.assertEqual( gp.value[ 'r2' ][ 'bitFields' ][ 'f2' ][ 'name' ], 'f2' )
        self.assertEqual( gp.value[ 'r2' ][ 'bitFields' ][ 'f2' ][ 'bitRange' ].value, [ 7, 7 ] )


    def testFromBadYamlData( self ) :
        yamlData = { 'mode' : 'ro' }
        with self.assertRaisesRegex( rmd.ParseError, '^Registers not defined in yaml data' ) :
            rmd.RegistersParameter.from_yamlData( yamlData, self.module, self.memorySpace )


    def testOptionalYamlData( self ) :
        yamlData = { 'mode' : 'ro' }
        gp = rmd.RegistersParameter.from_yamlData( yamlData, self.module, self.memorySpace,
                                                   optional = True )


if __name__ == '__main__' :
    unittest.main( )
