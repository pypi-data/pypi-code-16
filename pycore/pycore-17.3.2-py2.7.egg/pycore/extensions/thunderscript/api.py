"""
Copyright (c) 2014 Maciej Nabozny

This file is part of CloudOver project.

CloudOver is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pycore.extensions.vpn.models.vpn
from pycore.utils import request, calc_hash

class Api():
    def __init__(self, parent_model):
        self.parent_model = parent_model

    def call(self, script, variables):
        ret = request(self.oc_address, '/api/thunder/call/', {'token': self.token,
                                                              'script': script,
                                                              'variables': variables}, self.debug)
        return ret


    def variables(self, script):
        ret = request(self.oc_address, '/api/thunder/call/', {'token': self.token,
                                                              'script': script}, self.debug)
        return ret
