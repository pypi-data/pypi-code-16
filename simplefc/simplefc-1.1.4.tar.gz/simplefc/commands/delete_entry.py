"""Delete entries from flashcard sets."""
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


class Delete_entry(Base):

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
        IDs = self.options.get('<ID>')
        
        print('\n(ID, term, correct, incorrect, archived)')
        for i in IDs:
            cards = cur.execute("select ID, term, correct, "
                                "incorrect, archived from " +name+
                                " where ID is " +i+ ";")
            [print(j) for j in cards]
 
        choice = input("\nReally delete?\n(y/n)\n>")
        
        if choice == 'y':
            for i in IDs:
                cur.execute("delete from " +name+ " where ID is "
                            +i+ ";")
            if len(IDs) > 1:
                print('Entries deleted.')
            else:
                print('Entry deleted.')
        elif choice == 'n':
            print('Aborted.')
        else:
            print("required input either 'y' or 'n'.")

        conn.commit()
        conn.close()
