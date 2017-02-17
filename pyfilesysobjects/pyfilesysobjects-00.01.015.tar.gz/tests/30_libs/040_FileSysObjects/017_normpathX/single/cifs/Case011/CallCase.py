from __future__ import absolute_import


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


class CallUnits(unittest.TestCase):
    pass

    def testCase000(self):
        apstr = filesysobjects.FileSysObjects.normpathX('//hostname/share/a/b/c',**{'tpf':'win'})
        retRef = ('SHARE','hostname', 'share', filesysobjects.FileSysObjects.normpathX('a/b/c',**{'tpf':'posix'}))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**{'tpf':'posix'})
        self.assertEqual(retRef, ret) 
        
    def testCase010(self):
        apstr = 'cifs://'+filesysobjects.FileSysObjects.normpathX('hostname/share/a/b/c',**{'tpf':'win'})
        retRef = ('CIFS','hostname', 'share', filesysobjects.FileSysObjects.normpathX('a/b/c',**{'tpf':'posix'})) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**{'tpf':'posix'})
        self.assertEqual(retRef, ret) 
 
    def testCase020(self):
        apstr = 'file://///'+filesysobjects.FileSysObjects.normpathX('hostname/share/a/b/c',**{'tpf':'win'})
        retRef = ('SHARE','hostname', 'share', filesysobjects.FileSysObjects.normpathX('a/b/c',**{'tpf':'posix'})) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**{'tpf':'posix'})
        self.assertEqual(retRef, ret) 


#
#######################
#

if __name__ == '__main__':
    unittest.main()

