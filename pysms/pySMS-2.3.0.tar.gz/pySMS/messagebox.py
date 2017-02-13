# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 16:16:58 2016

@author: doarni
"""

import ctypes as c


def msgBox(msg, title, button, icon):
    dictButtons = {'MB_OK': 0x0,
                    'MB_OKCXL': 0x01,
                    'MB_YESNOCXL': 0x03,
                    'MB_YESNO': 0x04,
                    'MB_HELP': 0x4000}
                    
    dictIcons = {'ICON_EXCLAIM': 0x30,
                 'ICON_INFO': 0x40,
                 'ICON_STOP': 0x10}
    
    dictIDS = {'IDOK': 0,
               'IDCANCEL':  2,
               'IDABORT': 3,
               'IDYES': 6,
               'IDNO': 7}
            
    c.windll.user32.MessageBoxW(0, title, msg, dictButtons[button] | dictIcons[icon])

