from __future__ import absolute_import
from linecache import getline

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,sys

import filesysobjects.FileSysObjects

#
#######################
#


class CheckEscUnesc(unittest.TestCase):

    def __init__(self,*args,**kargs):
        self.printit = False
        super(CheckEscUnesc,self).__init__(*args,**kargs)

    def check_esc_unesc(self,_in,_esc,_unesc,tps=None):
        if self.printit:
            print 'Test:'
        l0 = len(_in)
        l1 = len(_esc)
        l2 = len(_unesc)

        ret0 = filesysobjects.FileSysObjects.escapeFilePath(_in,tps)
        lr0 = len(ret0)
        if self.printit:
            print "#---l0 ="+str(l0)
            print "#---lr0="+str(lr0)
            print '  _in = "'+ str(_in) +'"'
            for s in _in: print str(s)+" = "+ str(id(s)) + " ord(" + str(ord(s)) + ")  " + str(s)
            print "#---"
            print '  ret0 = "'+ str(ret0) +'"'
            for s in ret0: print str(s)+" = "+ str(id(s)) + " ord(" + str(ord(s)) + ")  " + str(s)
            print "#---"
        self.assertEqual(_esc, ret0) 

        ret1 = filesysobjects.FileSysObjects.unescapeFilePath(ret0)
        lr1 = len(ret1)
        if self.printit:
            print "#---l1 ="+str(l1)
            print "#---lr1="+str(lr1)
            print '  _unesc = "'+ str(_unesc) +'"'
            for s in _unesc: print str(s)+" = "+ str(id(s)) + " ord(" + str(ord(s)) + ")  " + str(s)
            print "#---"
            print '  ret1 = "'+ str(ret1) +'"'
            for s in ret1: print str(s)+" = "+ str(id(s)) + " ord(" + str(ord(s)) + ")  " + str(s)
        self.assertEqual(_unesc, ret1) 

