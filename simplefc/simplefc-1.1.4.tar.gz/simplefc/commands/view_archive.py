"""View archived entries within a flashcard set."""
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

class View_archive(Base):

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
        name = str(self.options.get('<setname>'))
        cards = cur.execute("select ID, term, correct, "
                            "incorrect from " +name+ " where archived "
                            "is 'Y';")

        print('(ID, term, correct, incorrect)')
        for i in cards:
            print(i)

        conn.commit()
        conn.close()
