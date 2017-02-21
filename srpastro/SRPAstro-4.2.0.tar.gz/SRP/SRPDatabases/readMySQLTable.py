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

import mysql.connector as pm
from astropy.table import Table


def readMySQLTable (host=ihost, database=idbase, user=iuser, password=ipwd, query=icmd):
    db = pm.connect(user=iuser, password=ipwd, host=ihost, database=idbase)
    cursor = db.cursor()
    cursor.execute(icmd)
    cols = cursor.column_names
    dt = [a for a in cursor]
    t = Table(rows=dt,names=cols)
    return t

