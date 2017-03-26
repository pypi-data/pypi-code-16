########################################################################################
##
## pyKStroke - Simple keyboard input hook on multiple platforms that returns a character.
## Copyright (C) 2014  Tungsteno <contacts00-pykstroke@yahoo.it>
##
## https://bitbucket.org/Tungsteno/pykstroke/wiki/Home
##
## This file is part of pyKStroke.
##
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with pyKStroke.  If not, see <http://www.gnu.org/licenses/>.
##
########################################################################################

import win32gui
import os
import win32process
from ksSystem.SysGetchWindows import _GetchWindows as _SysGetchWindows

class _GetchWindows(_SysGetchWindows):
    """Gets a single character from standard input. 
Returns a tuple with (unicode char, event type code)
Implementation for Win32 like systems
    
    """
    def __init__(self):
        self._pywindow = self._window_to_pid(os.getpid())

    def _window_to_pid(self, pid):
        """Find the window associated with the actual python process """
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    hwnds.append(hwnd)
            return True
    
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds

    def _event_core(self, event, state):
        if event.Window in self._pywindow:
            _SysGetchWindows._event_core(self, event, state)
        return self._exit_event()