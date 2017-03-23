#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2017 Chintalagiri Shashank
# Released under the MIT license.

"""
Docstring for serve_ftp

TODO : Migrate to pyfilesystem2 instead and modify the twisted FTP Factory to
  serve files from the file system object instead of FUSE mounting.
"""

from twisted.protocols import ftp
from twisted.application import service
from twisted.internet import reactor
from twisted.cred.portal import Portal
from twisted.cred.checkers import AllowAnonymousAccess

from fs.opener import fsopendir
from fs.mountfs import MountFS
from fs.expose import fuse
from fs.osfs import OSFS

from config import FTP_FILESYSTEMS
from config import FTP_PORT


class FTPService(service.Service):
    def __init__(self, portnum, filesystems):
        self._portnum = portnum
        self._filesystems = filesystems
        self._port = None
        self._fs = None

    def prep_filesystems(self):
        mountfs = OSFS('/mnt/tendril-ftp-mp')
        stage = MountFS()
        for mp, root in FTP_FILESYSTEMS:
            fso = fsopendir(root, writeable=False)
            stage.mount(mp, fso)
        self._fs = fuse.mount(stage, mountfs.getsyspath('/'))
        print self._fs.path
        return

    def startService(self):
        print "Starting FTP Server"
        self.prep_filesystems()
        p = Portal(ftp.FTPRealm(anonymousRoot=self._fs.path),
                   [AllowAnonymousAccess()])
        self._port = reactor.listenTCP(self._portnum, ftp.FTPFactory(p))

    def stopService(self):
        self._fs.unmount()
        return self._port.stopListening()


def get_ftp_service():
    return FTPService(portnum=FTP_PORT, filesystems=FTP_FILESYSTEMS)
