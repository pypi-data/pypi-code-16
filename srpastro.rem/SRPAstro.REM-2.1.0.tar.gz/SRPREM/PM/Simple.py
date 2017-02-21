""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.2.0
Author  : Stefano Covino
Date    : 20/08/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (22/08/2012) First version.
        : (22/08/2013) Just offsets.
        : (20/08/2014) Porting to Pilar3.
"""



def Simple (xxx_todo_changeme, xxx_todo_changeme1):
    # AOFF: azimuth zero point correction
    # ZOFF: zenith distance zero point correction
    (az,alt) = xxx_todo_changeme
    (s_AOFF,s_ZOFF) = xxx_todo_changeme1
    zd = 90.0 - alt
    #
    naz = s_AOFF+az-az
    nzd = s_ZOFF+zd-zd
    return naz, -nzd

