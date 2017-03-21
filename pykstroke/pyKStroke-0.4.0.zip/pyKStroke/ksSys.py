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

"""ksSys.py module.

This module is used for detect any pressed key from any program.
Intercept any pressed key that occurs in the system and converts it in character even if this code is running in the background.
You could use this module if you are trying to do a keylogger-like program.
All __call__() methods of this module classes return the key code as unicode type.
Implementation for Unix/Linux/Windows/MacOs/OsX.
    Class list:
        KeyInput: Basic input class. Should be used if you need as input only a key or character.
        KeyEvent: Used for looping input keys. Should be used when you need multiple input key sequentially. Should not be used in conjunction with KeyThread class.
        KeyThread: Used with threading process. Should be used when you need a fast input response, independently from the main process execution.
        
"""

_import_error_str=""
try: 
    _import_error_str="for Windows systems: win32"
    from ksSystem.SysGetchWindows import _GetchWindows as _OSImpl
except ImportError: 
    try:
        _import_error_str="for Unix/Linux like systems: xlib"
        from ksSystem.SysGetchUnix import _GetchUnix as _OSImpl
    except ImportError:
        try:
            _import_error_str="for Mac Os9 systems: carbon"
            from ksSystem.SysGetchMacCarbon import _GetchMacCarbon as _OSImpl
        except ImportError:
            err="""Operating System not supported or module not present.
                 
Check following modules:   
            
            ""","      ",_import_error_str
            raise ImportError(err)


from __init__ import KeyInput, KeyEvent, KeyThread

KeyInput._OSImpl = _OSImpl

if __name__=='__main__':
    print "init test"
    #test=KeyInput()
    test=KeyEvent()
    #test=KeyThread()
    test._test()
