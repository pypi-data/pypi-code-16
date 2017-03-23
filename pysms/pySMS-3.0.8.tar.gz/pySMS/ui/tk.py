# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 10:12:16 2016

@author: doarni
"""


from tkinter import *


class widget():
    
    def __init__(self):
        self.val = None
         
    def entryBox(self, txt, hide=""):
        root = Tk()
        label1 = Label( root, text=txt)
        E1 = Entry(root, bd =5)
        E1.config(show=hide)
        def getStuff():
            self.val = (E1.get())
            root.destroy()
        submit = Button(root, text ="Ok", command = getStuff)
        submit.bind('<Return>', getStuff)
        label1.pack()
        E1.pack()
        E1.focus()
        submit.pack(side =BOTTOM) 

        root.call('wm', 'attributes', '.', '-topmost', True)
        root.after_idle(root.call, 'wm', 'attributes', '.', '-topmost', False)
        root.focus_force()     
        
        root.mainloop()
        
    
    def get(self, text, char=""):
        self.val = None
        self.entryBox(text, char)
        return self.val
        
