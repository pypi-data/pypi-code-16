"""Change the location of the database that holds your flashcards.
Simplefc will look there from now on. There doesn't
have to be a .db file already in that location."""
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
import re

class Change_dbpath(Base):

    def run(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = path.strip('commands')
        dbpfp = path + 'dbpath.txt'
        newpath = str(self.options.get('<newpath>'))
        if str(self.options.get('<newpath>')) == 'default':
            dbpathfile = open(dbpfp, 'w')
            dbpathfile.write(path+ 'simplefc.db')
            dbpathfile.close()
            print('Database file location changed.')
        else:
            try:
                re.search('.db$', newpath).group()
            except AttributeError:
                print("\nPath must end with the name of a "
                      "database file, e.g.:\n"
                      "'home/example/path/newlocation.db'.\n"
                      "There need not be an existing .db file "
                      "in the new location. You may also use "
                      "'default' in place of a path to restore "
                      "the default location and name:\n'" +path+
                      "simplefc.db'.")
            else:
                dbpathfile = open(dbpfp, 'w')
                dbpathfile.write(newpath)
                dbpathfile.close()
                print('Database file location changed.')
