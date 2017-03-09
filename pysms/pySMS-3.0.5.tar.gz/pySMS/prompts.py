# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 17:08:22 2016

@author: doarni
"""
from pySMS.ui.tk import widget

class prompts():
    
    def loginInfo():
        w = widget()
        username = input("Username: ")
        password = w.get('Password', "*")
        return username, password
