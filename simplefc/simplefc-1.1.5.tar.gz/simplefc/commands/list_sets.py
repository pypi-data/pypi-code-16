"""List all flashcard sets."""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from .base import Base
import sqlite3
import os
import sys

class List_sets(Base):

    def run(self):
        path = os.path.dirname(os.path.realpath(__file__))
        dbpfp = path + '/../dbpath.txt'
        if not os.path.exists(dbpfp):
            sys.exit("No database file detected. Use "
                     "'simplefc create_set <setname>' to get "
                     "started.")
        dbpathfile = open(dbpfp, 'r')
        dbpath = dbpathfile.read()
        dbpathfile.close()
        conn = sqlite3.connect(dbpath)
        cur = conn.cursor()
        sets = cur.execute("select name from sqlite_master where "
                           "type = 'table' and name is not "
                           "'sqlite_sequence';")

        for i in sets:
            print(i[0])

        conn.commit()
        conn.close()
