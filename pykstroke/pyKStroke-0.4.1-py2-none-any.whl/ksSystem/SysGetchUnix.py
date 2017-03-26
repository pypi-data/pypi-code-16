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

import ctypes
from Xlib.display import Display
from Xlib import X, XK
from Xlib.ext import record
from Xlib.protocol import rq



#State of modified keys: unshift,shift,lock,alt gr,shift+alt gr,numlock. (can be more efficent?)
# numlock=16
# shift=1
# lock=2
# alt gr=128
# ctrl=4
# alt=8
KEY_STATE_BIND={
                #no active modifier
                    0:0, #unshifted
                #base state modifiers
                    1:1, #shifted
                    128:2, #alt gr
                    129:3, #shif+alt gr
                #numlock active
                    16:0, #as unshifted
                    17:1, #as shifted
                    144:2, #as alt gr
                    145:3, #as shif+alt gr
                    25:1, # as shifted (shift+alt)
                #lock active
                    3:0, #as unshifted
                    2:1, #as shifted
                    130:2, #as alt gr
                    131:3, #as shif+alt gr
                    27:0, #as unshifted
                    11:0, #as unshifted (shift+alt)
                #lock + numlock active
                    19:0, #as unshifted
                    18:1, #as shifted
                    146:2, #as alt gr
                    147:3, #as shift+alt gr
                    27:0, #as unshifted (shift+alt)
                #lock + numlock + ctrl active
                    23:0, #as unshifted
                    22:1, #as shifted
                    150:2, #as alt gr
                    151:3, #as shift+alt gr
                #ctrl active
                    4:0, #as unshifted
                    20:0, #as unshifted (numlock)
                    5:1, #as shifted (shift)
                    12:2, #as alt gr 
                    132:2, #as alt gr
                    13:3, #as shift+alt gr (shift+alt)
                    15:3, #as shift+alt gr (shift+alt+lock)
                    29:3, #as shift+alt gr (shift+alt+numlock)
                    31:3, #as shift+alt gr (shift+alt+lock+numlock)
                #other combo active
                    9:1, #as shifted
               }

class _GetchUnix: 
    """Gets a single character from standard input. 
Returns a tuple with (unicode char, event type code)
Implementation for Unix/linux like systems
        
    """
    def __init__(self): 
        # get current display
        self.disp = Display()
        #root = self.disp.screen().root #window?

        self.ctx = self.disp.record_create_context(
                0,
                [record.AllClients],
                [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (X.KeyPress, X.KeyRelease), #code 2 and 3
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
                }])
     
    def __call__(self): 
        self._exit=False
        # Monitor keypress and button press
        try:
            self.disp.record_enable_context(self.ctx, self._on_keyboard_event)
        except KeyboardInterrupt:
            pass
        finally:
            self.disp.record_disable_context(self.ctx)
            self.disp.flush()
            self.disp.record_free_context(self.ctx)
            self.disp.close()

    def set_exit(self,boolvalue):
        """Set the _ExitEvent() to True or False. You need to set it if you would exit from the key handler or continue it."""
        if type(boolvalue)== bool:
            self._exit=boolvalue
        else:
            raise TypeError("*boolvalue* parameter must be boolean")

    def _exit_event(self):
        if self._exit:
            raise KeyboardInterrupt #search for a best mode to disable the loop handler.

    def key_event(self):
        pass

    def _on_keyboard_event(self,reply):
        """This function is called when a xlib event is fired. """
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, self.disp.display, None, None)  
            key=self.disp.keycode_to_keysym(event.detail, KEY_STATE_BIND.get(event.state,4)) #find a xlib native KEY_STATE_BIND like method (more efficently).  
            if key>=0xFF00: #Convert keysym special keys to unicode/ascii special keys. Find native Xlib method for do this. (more efficently).
                if key!=0xFFFF:
                    key=key-0xFF00
                else:
                    key=0x007F #hexadecimal unicode/ascii code for DEL character.
                      
            self._retkey=(key,event.type-2) #KeyPress 2-2=0, KeyRelease 3-2=1. errors if negative numbers
 
            # KEYCODE IS FOUND USING event.detail  
            self.key_event()
 
            self._exit_event()

