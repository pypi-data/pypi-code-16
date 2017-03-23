# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 15:16:15 2016

@author: doarni
"""

import pyHook
from pyHook import HookManager, GetKeyState, HookConstants
import pySMS.keys as keys
import pythoncom
import sys

def OnKeyboardEvent(event):
    # in case you want to debug: uncomment next line
    # print repr(event), event.KeyID, HookConstants.IDToName(event.KeyID), event.ScanCode , event.Ascii, event.flags
    if GetKeyState(HookConstants.VKeyToID('VK_LSHIFT')) and event.KeyID == HookConstants.VKeyToID('VK_SNAPSHOT'):
        print("shift + snapshot pressed")
    elif GetKeyState(HookConstants.VKeyToID('VK_CONTROL')) and HookConstants.IDToName(event.KeyID) == 'D':
        print("ctrl + d pressed")
        sys.exit()
    elif GetKeyState(HookConstants.VKeyToID(keys.VK_LALT)) and HookConstants.IDToName(event.KeyID) == 'Q':
        print("alt + q pressed")
        
    return True


if __name__ == '__main__':
    hm = pyHook.HookManager()
    hm.KeyDown = OnKeyboardEvent
    hm.HookKeyboard()
    pythoncom.PumpMessages()
else:
    print("This module cannot be imported")
    print('This it to be used to test pyHook')
    raise ImportError
