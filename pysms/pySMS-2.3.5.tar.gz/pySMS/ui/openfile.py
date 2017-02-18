# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 12:02:33 2016

@author: doarni
"""

from tkinter import *
from tkinter.filedialog import askopenfilename   

fname = "unassigned"

def dialog():    
    def openFile():
        global fname
        fname = askopenfilename(filetypes = (("Excel files", "*.xlsx;*.xls"),
                                             ("All files", "*.*")))
        root.destroy()

    root = Tk()
    Button(root, text='Load file', command = openFile).pack(fill=X)
    mainloop()
    return fname
    
    


    