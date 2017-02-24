# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 09:53:07 2016

@author: doarni
"""

import subprocess
import importlib

class Prereq():
    
    def __init__(self):
        self.req_mod_list = ['selenium',
                             'colorama',
                             'binascii',
                             'lxml',
                             'xlrd',
                             'prettytable',
                             'cssselect',
                             'pythoncom',
                             'psycopg2']
                                 
    def importer(self):
        print('Checking for required modules')
        list = []
        for module in self.req_mod_list:
            try:
                print('Checking for ' + module)
                importlib.import_module(module)
                print(module + ' imported successfully')
            except:
                print('Unable to import ' + module)
                list.append(module)
        #self.install(list)
        print('Unable to locate the following modules:')
        i = 1
        for item in list:
            print(str(i) + ") " + item)

        if input('Install them now? Y/N: ').upper() == 'Y':
            self.install(list)
        else:
            pass

    def install(self, list):
        for item in list:
            subprocess.call(['pip','install',item])
 
    def update(self):
        for item in self.req_mod_list:
            subprocess.call(['pip','install',item,'--upgrade'])
     
def import_pkgs():
    pr = Prereq()
    pr.importer()
    
def upgrade_pkgs():
    pr = Prereq()
    pr.update()    
    
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description = 'Build program latest version')
    parser.add_argument('-up','--update', action='store_true', help='Update / Install Required Modules', required=False)
    parser.add_argument('-ug','--upgrade', action='store_true', help='Update Required Modules', required=False)

    args = vars(parser.parse_args())
    
    if args['update']:      
        import_pkgs()
    
    if args['upgrade']:      
        upgrade_pkgs()
        