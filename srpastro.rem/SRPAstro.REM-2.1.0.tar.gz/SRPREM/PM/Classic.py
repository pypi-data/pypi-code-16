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

import numpy


def cotg (ang):
    return 1./numpy.tan(ang)


def Classic (xxx_todo_changeme, xxx_todo_changeme1):
    # AN: error in the leveling of the telescope toward north
    # AE: error in the leveling of the telescope toward east
    # NPAE: non-perpendicularity of the azimuth and elevation axis
    # BNP: non-perpendicularity of the optical and the elevation axis
    # TF: sagging of the tube
    # AOFF: azimuth zero point correction
    # ZOFF: zenith distance zero point correction
    (az,alt) = xxx_todo_changeme
    (c_AN,c_AE,c_NPAE,c_BNP,c_TF,c_AOFF,c_ZOFF) = xxx_todo_changeme1
    zd = 90.0 - alt
    #
    azr = numpy.radians(az)
    zdr = numpy.radians(zd)
    #
    naz = -c_AN * numpy.sin(azr) * cotg(zdr) + c_AE * numpy.cos(azr) * cotg(zdr) + c_NPAE * cotg(zdr) - c_BNP / numpy.sin(zdr) + c_AOFF
    nzd = c_AN * numpy.cos(azr) + c_AE * numpy.sin(azr) + c_TF * numpy.sin(zdr) + c_ZOFF
    return naz, -nzd

