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

import registerMap.utility.observer as rmo


class MockObserver( rmo.Observer ) :
    def __init__( self ) :
        self.arguments = None
        self.updateCount = 0


    @property
    def updated( self ) :
        isUpdated = False
        if self.updateCount != 0 :
            isUpdated = True
        return isUpdated


    def update( self, source, arguments ) :
        self.updateCount += 1
        self.arguments = arguments
