"""Sebureem Command Line Utilities

Usage:
    sebureem serve [--debug] [<host>] [<port>]
    sebureem database (--init)

Options:
    --debug         Start the bottle app in debug mode.
    --init          Initialize database.
    -h --help       Show this screen.
    --version       Show version.

"""
from docopt import docopt

from sebureem import serve, db
from sebureem.models import *

def sebureem():
    args = docopt(__doc__, version='0.0.1')

    if args['serve']:
        serve(
            args['<host>'] or "localhost", 
            args['<port>'] or "8080",
            args['--debug']
        )
    elif args['database']:
        if args['--init']:
            create_db()

def create_db():
    db.connect()
    db.create_tables([Sebura, Sebuks])
    db.close()

