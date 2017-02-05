#
# Copyright 2017 Russell Smiley
#
# This file is part of timetools.
#
# timetools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# timetools is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with timetools.  If not, see <http://www.gnu.org/licenses/>.
#

import multiprocessing
import multiprocessing.pool


# From http://stackoverflow.com/questions/6974695/python-process-pool-non-daemonic/8963618#8963618
class NoDaemonProcess(multiprocessing.Process):
    # Make 'daemon' attribute always return False in order to be able to create a hierarchy of multiprocessing jobs.
    def _get_daemon(self):
        return False
    
    
    def _set_daemon(self, value):
        pass
    
    
    daemon = property(_get_daemon, _set_daemon)
    

class NoDaemonPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess
