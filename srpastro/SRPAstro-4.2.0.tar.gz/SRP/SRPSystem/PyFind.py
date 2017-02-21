""" Utility functions and classes for SRP

Context : SRP
Module  : System.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 02/04/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Usage   : PyFind (path, selp='*')
            

History : (02/04/2016) First version.

"""


import os, fnmatch


def PyFind (path, selp='*', exclp=''):
    fileList = []
    #
    for dName, sdName, fList in os.walk(path):
        for fileName in fList:
            if fnmatch.fnmatch(fileName, selp) and not fnmatch.fnmatch(fileName, exclp):
                fileList.append(os.path.join(dName, fileName))
    #
    return fileList
