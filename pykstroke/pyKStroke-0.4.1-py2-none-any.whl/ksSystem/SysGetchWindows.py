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

import pythoncom #part of pywin32 package
import pyHook
import ctypes

class _GetchWindows: 
    """Gets a single character from standard input. 
Returns a tuple with (unicode char, event type code)
Implementation for Win32 like systems
    
    """
    def __init__(self):
        pass

    def __call__(self):
        hm = pyHook.HookManager() 
        hm.KeyUp = self._on_keyboard_event_up  
        hm.KeyDown = self._on_keyboard_event_down
        self._exit=False
        try:
            hm.HookKeyboard()
            pythoncom.PumpMessages()
        finally:
            hm.UnhookKeyboard()

    def set_exit(self, boolvalue):
        """Set the _ExitEvent() to True or False. You need to set it if you would exit from the key event loop or continue it. """
        if type(boolvalue)== bool:
            self._exit=boolvalue
        else:
            raise TypeError("*boolvalue* parameter must be boolean")

    def _exit_event(self):
        if self._exit:
            ctypes.windll.user32.PostQuitMessage(0)
            return False
        else:
            return True

    def key_event(self):
        pass

    def _event_core(self, event, state):
        self._retkey = (event.Ascii, state) #state code follow X11 coding
        self.key_event()
        return self._exit_event()

    def _on_keyboard_event_up(self, event):
        """This function is called when a windows event keyup is fired. """
        return self._event_core(event,0)

    def _on_keyboard_event_down(self, event):
        """This function is called when a windows event keydown is fired. """
        return self._event_core(event,1)





