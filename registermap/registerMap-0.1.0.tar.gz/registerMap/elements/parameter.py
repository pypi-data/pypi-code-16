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

import registerMap.elements.constraint as rmc
import registerMap.utility.yaml.encode as rye

from registerMap.exceptions import ParseError


class Parameter :
    def __init__( self,
                  name = None,
                  value = None ) :
        self.name = name
        self.value = value


    def validate( self, value ) :
        # By default, do nothing (implicitly pass validation)
        pass


    @classmethod
    def from_yamlData( cls, yamlData, name,
                       optional = False ) :
        parameter = cls( )
        parameter.name = name

        if name in yamlData.keys( ) :
            # Don't modify the data type discovered by yaml parsing.
            parameter.value = yamlData[ name ]
        elif optional :
            parameter.value = None
        elif not optional :
            raise ParseError( 'Parameter is not in yaml data, ' + repr( name ) )

        return parameter


    def to_yamlData( self ) :
        # Assume the data can be stored directly in yaml.
        yamlData = rye.parameter( self.name, self.value )
        return yamlData


class ConstraintsParameter( Parameter ) :
    __parameterName = 'constraints'


    def __init__( self, memorySpace ) :
        super( ).__init__( self.__parameterName, rmc.ConstraintTable( memorySpace ) )


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace,
                       optional = False ) :
        parameter = cls( memorySpace )
        parameter.value = rmc.ConstraintTable.from_yamlData( yamlData, memorySpace,
                                                             optional = optional )
        return parameter


    def to_yamlData( self ) :
        return self.value.to_yamlData( )
