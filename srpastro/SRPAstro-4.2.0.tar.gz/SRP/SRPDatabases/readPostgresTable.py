""" Utility functions and classes for SRP

Context : SRP
Module  : Databases.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 21/02/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : 

Remarks :

History : (21/02/2017) First version.
"""

import postgresql as ps
from astropy.table import Table


def readPostgresTable (host=ihost, database=idbase, user=iuser, password=ipwd, query=icmd):
    db = ps.open(host=ihost,database=idbase,user=iuser,password=ipwd)
    dbq = db.prepare(icmd)
    cols = dbq.column_names
    dt = [a for a in dbq]
    t = Table(rows=dt,names=cols)
    return t

