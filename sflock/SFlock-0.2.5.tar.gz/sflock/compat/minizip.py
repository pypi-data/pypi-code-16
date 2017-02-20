# Copyright (C) 2016 Jurriaan Bremer.
# This file is part of SFlock - http://www.sflock.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os
import tempfile

import shutil

try:
    import pyminizip
    HAVE_PYMINIZIP = True
except ImportError:
    HAVE_PYMINIZIP = False

class MiniZipFile(object):
    def __init__(self, tmpdir=None):
        self.password = None
        self.contents = []
        self.dirpath = tempfile.mkdtemp()

        if not HAVE_PYMINIZIP:
            raise RuntimeError("Can't use MiniZipFile on this platform!")

    def setpassword(self, password):
        self.password = password

    def writestr(self, filename, content):
        dirname = os.path.dirname(filename)

        dirpath = os.path.join(self.dirpath, dirname)
        if dirname and not os.path.exists(dirpath):
            os.makedirs(dirpath)

        with open(os.path.join(self.dirpath, filename), "wb") as f:
            f.write(content)

    def write(self, filename, arcname):
        dirname = os.path.dirname(arcname)

        dirpath = os.path.join(self.dirpath, dirname)
        if dirname and not os.path.exists(dirpath):
            os.makedirs(dirpath)

        shutil.copy(filename, os.path.join(self.dirpath, arcname))

    def close(self):
        pass
