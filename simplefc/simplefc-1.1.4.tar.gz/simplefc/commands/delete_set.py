"""delete a flashcard set"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import input
from builtins import str
from future import standard_library
standard_library.install_aliases()
from .base import Base
import sqlite3
import os

class Delete_set(Base):

    def run(self):
        name = str(self.options.get('<setname>'))
        yn = input("Are you sure you want to delete flashcard set '"
                 + name + "'?\n(y/n)\n> ")
        if yn == 'y':
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
            cur.execute('drop table ' + name + ';')
            conn.commit()
            conn.close()
            print("deleted set '" + name + "'")

        elif yn == 'n':
            print("took no action")

        else:
            print("required input either 'y' or 'n'.")
