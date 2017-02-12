"""Set all 'correct' and 'incorrect' records back to 0."""
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

class Reset_data(Base):

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
        cur.execute("update " +name+ " set correct=0, "
                    "incorrect=0;")
        
        print("Correct/incorrect count has been reset "
              "for flashcard set '" +name+ "'.")

        conn.commit()
        conn.close()
