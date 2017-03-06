# Copyright (C) 2017 Michał Góral.
#
# This file is part of Feed Commas
#
# Feed Commas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Feed Commas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Feed Commas. If not, see <http://www.gnu.org/licenses/>.

'''Utility functions'''

import os
import errno

def mkdir_p(path):
    '''Works like `mkdir -p`: creates all (not yet existing) directories in a
    given path.'''
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
