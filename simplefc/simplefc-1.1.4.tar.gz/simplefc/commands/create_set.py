"""create a new flashcard set"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import str
from future import standard_library
standard_library.install_aliases()
from .base import Base
import sqlite3
import os

class Create_set(Base):

    def run(self):
        path = os.path.dirname(os.path.realpath(__file__))
        dbpfp = path + '/../dbpath.txt'
        if not os.path.exists(dbpfp):
            dbpathfile = open(dbpfp, 'w+')
            path = path.strip('commands')
            dbpathfile.write(path + 'simplefc.db')
            dbpathfile.close()
        dbpathfile = open(dbpfp, 'r')
        dbpath = dbpathfile.read()
        dbpathfile.close()
        conn = sqlite3.connect(dbpath)
        cur = conn.cursor()
        name = str(self.options.get('<setname>'))
        cur.execute("create table if not exists " + name +
                    """ (ID integer primary 
                    key autoincrement, term text, definition text, 
                    correct integer default 0, incorrect integer default
                    0, archived text default 'N');""")

        print("Created new flashcard set '" +name+ "'.")

        conn.commit()
        conn.close()
