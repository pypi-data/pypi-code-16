# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 00:06:01 2016

@author: doarni
"""
from prettytable import PrettyTable
from colorama import init, Fore
init(autoreset=True)

class tables():
    
    def intro():
        x = PrettyTable()
        
        def colorTxt(txt):
            return Fore.LIGHTCYAN_EX + txt
        
        x.field_names = [colorTxt("Credentials")]
        x.add_row([colorTxt("Please Login with your SMS credentials.")])
        x.align = "l"
        x.junction_char = '#'
        
        print(x)
        
    def head():
        x = PrettyTable()
       
        def colorTxt(txt):
            return Fore.LIGHTGREEN_EX + txt
        x.field_names = [colorTxt("PYSMS MACROS FOR ZBSMS")]
        x.add_row([colorTxt("pySMS is a keyboard macro program")])
        x.add_row([colorTxt("to make navigating ZBSMS faster ")])
        x.add_row([colorTxt("and more intuitive. Press F10")])
        x.add_row([colorTxt("for a list of commands!")])
        x.add_row([colorTxt("Created by: Ian Doarn")])
        x.add_row([colorTxt("EMAIL: Ian.Doarn@zimmerbiomet.com")])
        x.align = "l"
        x.junction_char = '%'
        x.padding_width = 0
        print(x)
            
    def stockTableDisplay(p, d, ls, ct, lc, lt):
        x = PrettyTable()
        
        def whiteTxt(txt):
            return Fore.LIGHTWHITE_EX + txt

        def greenTxt(txt):
            return Fore.LIGHTGREEN_EX + txt
        
        x.field_names = [greenTxt("Product"), 
                         greenTxt("Desc"), 
                         greenTxt("Lot // Serial Number"), 
                         greenTxt("Container"), 
                         greenTxt("Location"),
                         greenTxt("Location Type")]
                         
        x.add_row([whiteTxt(p), 
                   whiteTxt(d), 
                   whiteTxt(ls), 
                   whiteTxt(ct), 
                   whiteTxt(lc), 
                   whiteTxt(lt)])
                   
        x.align = "l"
        x.junction_char = '*'
        x.padding_width = 0
        print(x)
    
    def formatDictotList(dict):
        list = []
        for key, val in dict.items():
            list.append((str(key) + ': ' , str(val)))
        return list
        
    def formatListToTable(dict, listX, color):
        string = ""
        list = []
        for a in range(len(listX)):
            list.append(listX[a][0] + color + listX[a][1])
        for i in range(len(list[0]) + 5):
            string = string + "-"
        print(string)
        for item in range(len(list)):
            print('> ' + list[item], sep=' | ')
        print(string)

