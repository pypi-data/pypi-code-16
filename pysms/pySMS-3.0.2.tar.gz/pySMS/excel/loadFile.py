# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 12:30:48 2016

@author: doarni
"""


import pySMS.excel.ui.openfile as op
import os

class openFile():
    
    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.fname = None
        
    def openFileDialog(self):
        self.fname = op.dialog()
        return self.fname
