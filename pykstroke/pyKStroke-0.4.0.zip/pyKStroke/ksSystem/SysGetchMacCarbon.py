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

#NO TESTED CODE HERE

import Carbon 
import Carbon.Evt #see if it has this (in Unix, it doesn't) 
from Carbon.Evt import EventAvail, GetNextEvent

class _GetchMacCarbon: 
    """Gets a single character from standard input. 
Returns a tuple with (unicode char, event type code)
Implementation for older version of Mac (Os9) systems

    """ 
    def __init__(self): 
        self._exit=False

    def set_exit(self,boolvalue):
        """Set the _ExitEvent() to True or False. You need to set it if you would exit from the key event loop or continue it."""
        if type(boolvalue)== bool:
            self._exit=boolvalue
        else:
            raise TypeError("*boolvalue* parameter must be boolean") 

    def key_event(self):
        pass

    def __call__(self): 
        while not self._exit:
            if EventAvail(0x0008)[0]!=0: # 0x0008 is the keyDownMask, 0x0010 is the KeyUpMask (keyDown = 3, keyUp = 4)
                (what,msg,when,where,mod)=GetNextEvent(0x0008)[1] 
                self._retkey=((msg & 0x000000FF),1) 
                self.key_event()            
            elif EventAvail(0x00010)[0]!=0:
                (what,msg,when,where,mod)=GetNextEvent(0x00010)[1] 
                self._retkey=((msg & 0x000000FF),0) 
                self.key_event() 
            else:
                self._exit=True
