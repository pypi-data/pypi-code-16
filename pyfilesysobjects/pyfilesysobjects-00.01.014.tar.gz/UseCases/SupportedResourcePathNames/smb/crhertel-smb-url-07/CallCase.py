from __future__ import absolute_import
from linecache import getline

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,platform
import tests.CheckEscUnesc

from filesysobjects.FileSysObjects import normpathX
#
#######################
#


class UseCase(tests.CheckEscUnesc.CheckEscUnesc):

    def testCase040(self):
        _in        = r'smb://'
        _esc     = r'smb://'
        _unesc = r'smb://'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase050(self):
        _in        = r'smb://smb_browse/'
        _esc     = r'smb://smb_browse'
        _unesc = r'smb://smb_browse'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase060(self):
        _in        = r'smb://smb_server/'
        _esc     = r'smb://smb_server'
        _unesc = r'smb://smb_server'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase070(self):
        _in        = r'smb://smb_server/abs_path'
        if platform.system() == 'Windows':
            _esc     = r'smb://smb_server\\abs_path'
            _unesc = r'smb://smb_server\abs_path'
        else:
            _esc     = r'smb://smb_server/abs_path'
            _unesc = r'smb://smb_server/abs_path'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase080(self):
        _in        = r'smb://netbios.scope.id/'
        _esc     = r'smb://netbios.scope.id'
        _unesc = r'smb://netbios.scope.id'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase090(self):
        _in        = r'smb://netbios/?SCOPE=scope.id'
        if platform.system() == 'Windows':
            _esc     = r'smb://netbios\\?SCOPE=scope.id'
            _unesc = r'smb://netbios\?SCOPE=scope.id'
        else:
            _esc     = r'smb://netbios/?SCOPE=scope.id'
            _unesc = r'smb://netbios/?SCOPE=scope.id'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase100(self):
        _in        = r'smb://jcifs/?CALLED=VIRTSERV;NBNS=172.24.19.18'
        if platform.system() == 'Windows':
            _esc     = r'smb://jcifs\\?CALLED=VIRTSERV;NBNS=172.24.19.18'
            _unesc = r'smb://jcifs\?CALLED=VIRTSERV;NBNS=172.24.19.18'
        else:
            _esc     = r'smb://jcifs/?CALLED=VIRTSERV;NBNS=172.24.19.18'
            _unesc = r'smb://jcifs/?CALLED=VIRTSERV;NBNS=172.24.19.18'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase110(self):
        _in        = r'smb://smedley/?NBNS=172.24.19.18;NODETYPE=H'
        if platform.system() == 'Windows':
            _esc     = r'smb://smedley\\?NBNS=172.24.19.18;NODETYPE=H'
            _unesc = r'smb://smedley\?NBNS=172.24.19.18;NODETYPE=H'
        else:
            _esc     = r'smb://smedley/?NBNS=172.24.19.18;NODETYPE=H'
            _unesc = r'smb://smedley/?NBNS=172.24.19.18;NODETYPE=H'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase120(self):
        _in        = r'smb://corgis/?NODETYPE=B'
        if platform.system() == 'Windows':
            _esc     = r'smb://corgis\\?NODETYPE=B'
            _unesc = r'smb://corgis\?NODETYPE=B'
        else:
            _esc     = r'smb://corgis/?NODETYPE=B'
            _unesc = r'smb://corgis/?NODETYPE=B'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase130(self):
        _in        = r'smb://jcifs.samba.org/?NODETYPE=;CALLED=SMBSERV'
        if platform.system() == 'Windows':
            _esc     = r'smb://jcifs.samba.org\\?NODETYPE=;CALLED=SMBSERV'
            _unesc = r'smb://jcifs.samba.org\?NODETYPE=;CALLED=SMBSERV'
        else:
            _esc     = r'smb://jcifs.samba.org/?NODETYPE=;CALLED=SMBSERV'
            _unesc = r'smb://jcifs.samba.org/?NODETYPE=;CALLED=SMBSERV'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase140(self):
        _in        = r'smb://bran/SCOPE='
        if platform.system() == 'Windows':
            _esc     = r'smb://bran\\SCOPE='
            _unesc = r'smb://bran\SCOPE='
        else:
            _esc     = r'smb://bran/SCOPE='
            _unesc = r'smb://bran/SCOPE='
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase150(self):
        _in        = r'smb://marika/SCOPE=;NODETYPE=B'
        if platform.system() == 'Windows':
            _esc     = r'smb://marika\\SCOPE=;NODETYPE=B'
            _unesc = r'smb://marika\SCOPE=;NODETYPE=B'
        else:
            _esc     = r'smb://marika/SCOPE=;NODETYPE=B'
            _unesc = r'smb://marika/SCOPE=;NODETYPE=B'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase160(self):
        _in        = r'//Specifying a drive and a file name'
        if platform.system() == 'Windows':
            _esc     = r'\\\\Specifying a drive and a file name'
            _unesc = r'\\Specifying a drive and a file name'
        else:
            _esc     = r'//Specifying a drive and a file name'
            _unesc = r'//Specifying a drive and a file name'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase170(self):
        _in        = r'file:///C|/My Documents/ALetter.html'
        if platform.system() == 'Windows':
            _esc     = r'file://\\C|\\My Documents\\ALetter.html'
            _unesc = r'file://\C|\My Documents\ALetter.html'
        else:
            _esc     = r'file:///C|/My Documents/ALetter.html'
            _unesc = r'file:///C|/My Documents/ALetter.html'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase180(self):
        _in        = r'//Specifying only a drive and a path to browse the directory'
        if platform.system() == 'Windows':
            _esc     = r'\\\\Specifying only a drive and a path to browse the directory'
            _unesc = r'\\Specifying only a drive and a path to browse the directory'
        else:
            _esc     = r'//Specifying only a drive and a path to browse the directory'
            _unesc = r'//Specifying only a drive and a path to browse the directory'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase190(self):
        _in        = r'file:///C|/My Documents/'
        if platform.system() == 'Windows':
            _esc     = r'file://\\C|\\My Documents'
            _unesc = r'file://\C|\My Documents'
        else:
            _esc     = r'file:///C|/My Documents'
            _unesc = r'file:///C|/My Documents'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase200(self):
        _in        = 'C:\My Documents\\'
        if platform.system() == 'Windows':
            _esc     = r'C:\\My Documents'
            _unesc = r'C:\My Documents'
        else:
            _esc     = r'C:/My Documents'
            _unesc = r'C:/My Documents'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase210(self):
        _in        = '\My Documents\\'
        _esc     = r'\\My Documents'
        _unesc = r'\My Documents'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')
 
    def testCase220(self):
        _in        = r'file:///Users/User/2ndFile.html'
        if platform.system() == 'Windows':
            _esc     = r'file://\\Users\\User\\2ndFile.html'
            _unesc = r'file://\Users\User\2ndFile.html'
        else:
            _esc     = r'file:///Users/User/2ndFile.html'
            _unesc = r'file:///Users/User/2ndFile.html'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase230(self):
        _in        = r'file:///C:/Users/User/2ndFile.html'
        if platform.system() == 'Windows':
            _esc     = r'file://\\C:\\Users\\User\\2ndFile.html'
            _unesc = r'file://\C:\Users\User\2ndFile.html'
        else:
            _esc     = r'file:///C:/Users/User/2ndFile.html'
            _unesc = r'file:///C:/Users/User/2ndFile.html'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase240(self):
        _in        = r'file://alpha.hut.fi/u/lai/tik/tik76002/public_html/lerman.files/chaps'
        if platform.system() == 'Windows':
            _esc     = r'file://alpha.hut.fi\\u\\lai\\tik\\tik76002\\public_html\\lerman.files\\chaps'
            _unesc = r'file://alpha.hut.fi\u\lai\tik\tik76002\public_html\lerman.files\chaps'
        else:
            _esc     = r'file://alpha.hut.fi/u/lai/tik/tik76002/public_html/lerman.files/chaps'
            _unesc = r'file://alpha.hut.fi/u/lai/tik/tik76002/public_html/lerman.files/chaps'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase250(self):
        _in        = r'file:///u/lai/tik/tik76002/public_html/lerman.files/chaps'
        if platform.system() == 'Windows':
            _esc     = r'file://\\u\\lai\\tik\\tik76002\\public_html\\lerman.files\\chaps'
            _unesc = r'file://\u\lai\tik\tik76002\public_html\lerman.files\chaps'
        else:
            _esc     = r'file:///u/lai/tik/tik76002/public_html/lerman.files/chaps'
            _unesc = r'file:///u/lai/tik/tik76002/public_html/lerman.files/chaps'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase260(self):
        _in        = r'file:///etc/motd'
        if platform.system() == 'Windows':
            _esc     = r'file://\\etc\\motd'
            _unesc = r'file://\etc\motd'
        else:
            _esc     = r'file:///etc/motd'
            _unesc = r'file:///etc/motd'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase270(self):
        _in        = r'file://localhost/absolute/path/to/file'
        if platform.system() == 'Windows':
            _esc     = r'file://localhost\\absolute\\path\\to\\file'
            _unesc = r'file://localhost\absolute\path\to\file'
        else:
            _esc     = r'file://localhost/absolute/path/to/file'
            _unesc = r'file://localhost/absolute/path/to/file'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase280(self):
        _in        = r'file://file_at_current_dir'
        _esc     = r'file://file_at_current_dir'
        _unesc = r'file://file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase290(self):
        _in        = r'file:///./file_at_current_dir'
        if platform.system() == 'Windows':
            _esc     = r'file://\\file_at_current_dir'
            _unesc = r'file://\file_at_current_dir'
        else:
            _esc     = r'file:///file_at_current_dir'
            _unesc = r'file:///file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase300(self):
        _in        = r'file:///foo.txt'
        if platform.system() == 'Windows':
            _esc     = r'file://\\foo.txt'
            _unesc = r'file://\foo.txt'
        else:
            _esc     = r'file:///foo.txt'
            _unesc = r'file:///foo.txt'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase310(self):
        _in        = r'file://foo.txt'
        _esc     = r'file://foo.txt'
        _unesc = r'file://foo.txt'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase320(self):
        _in        = r'file:///C:/autoexec.bat'
        if platform.system() == 'Windows':
            _esc     = r'file://\\C:\\autoexec.bat'
            _unesc = r'file://\C:\autoexec.bat'
        else:
            _esc     = r'file:///C:/autoexec.bat'
            _unesc = r'file:///C:/autoexec.bat'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase330(self):
        _in        = r'file:///C%3A/autoexec.bat'
        if platform.system() == 'Windows':
            _esc     = r'file://\\C%3A\\autoexec.bat'
            _unesc = r'file://\C%3A\autoexec.bat'
        else:
            _esc     = r'file:///C%3A/autoexec.bat'
            _unesc = r'file:///C%3A/autoexec.bat'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase340(self):
        _in        = r'smb://domain;username:passwor]@server/share/path'
        if platform.system() == 'Windows':
            _esc     = r'smb://domain;username:passwor]@server\\share\\path'
            _unesc = r'smb://domain;username:passwor]@server\share\path'
        else:
            _esc     = r'smb://domain;username:passwor]@server/share/path'
            _unesc = r'smb://domain;username:passwor]@server/share/path'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase350(self):
        _in        = r'smb://authdomain;user@host:port/share/dirpath/name?context'
        if platform.system() == 'Windows':
            _esc     = r'smb://authdomain;user@host:port\\share\\dirpath\\name?context'
            _unesc = r'smb://authdomain;user@host:port\share\dirpath\name?context'
        else:
            _esc     = r'smb://authdomain;user@host:port/share/dirpath/name?context'
            _unesc = r'smb://authdomain;user@host:port/share/dirpath/name?context'
        self.check_esc_unesc(_in,_esc,_unesc)


#
#######################
#

if __name__ == '__main__':
    unittest.main()

