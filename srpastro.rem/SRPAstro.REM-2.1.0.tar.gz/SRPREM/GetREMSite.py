""" get REM site information

Module  : SRPREM.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 10/05/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (31/08/2012) First version.
        : (10/05/2016) Better porting.
"""

import ephem
import SRPREM as SR


def GetREMSite ():
    site = ephem.Observer()
    site.lat = str(SR.REMLAT)
    site.long = str(SR.REMLONG)
    site.elevation = SR.REMHEIGHT
    return site