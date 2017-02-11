"""Show the path to the sqlite3 database file currently in use,
as well as the default db file location."""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from .base import Base
import os

class List_dbpath(Base):

    def run(self):
        path = os.path.dirname(os.path.realpath(__file__))
        dbpfp = path + '/../dbpath.txt'
        if not os.path.exists(dbpfp):
            sys.exit("No database file detected. Use "
                     "'simplefc create_set <setname>' to get "
                     "started.")
        dbpathfile = open(dbpfp, 'r')
        dbpath = dbpathfile.read()
        path = path.strip('commands')
        print('Current database file location:\n' + dbpath)
        print('\nDefault location:\n' +path+ 'simplefc.db')
