""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.3.0
Author  : Stefano Covino
Date    : 20/08/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (22/08/2012) First version.
        : (01/07/2013) Check of parameter names.
        : (22/08/2013) Just offsets.
        : (03/12/2013) Better naming of parameters.
        : (07/01/2014) Better organization of parameters.
        : (20/08/2014) Porting to Pilar3.
"""

import numpy

def cotg (ang):
    return 1./numpy.tan(ang)


def Full (xxx_todo_changeme, xxx_todo_changeme1):
    # AAN,ZAN: error in the leveling of the telescope toward north
    # AAE,ZAE: error in the leveling of the telescope toward east
    # NPAE: non-perpendicularity of the azimuth and elevation axis
    # BNP: non-perpendicularity of the optical and the elevation axis
    # AES, AEC, ZES, ZEC:  eccentricity of the encoders
    # AOFF: azimuth zero point correction
    # ZOFF: zenith distance zero point correction
    (az,alt) = xxx_todo_changeme
    (f_AAN,f_ZAN,f_AAE,f_ZAE,f_NPAE,f_BNP,f_AES,f_AEC,f_ZES,f_ZEC,f_AOFF,f_ZOFF) = xxx_todo_changeme1
    zd = 90.0 - alt
    #
    azr = numpy.radians(az)
    zdr = numpy.radians(zd)
    #
    naz = f_AAN * numpy.sin(azr) * cotg(zdr) - f_AAE * numpy.cos(azr) * cotg(zdr) + f_NPAE * cotg(zdr)  - f_BNP / numpy.sin(zdr) + f_AOFF + f_AES * numpy.sin(azr) + f_AEC * numpy.cos(azr)
    nzd = f_ZAN * numpy.cos(azr) + f_ZAE * numpy.sin(azr) + f_ZOFF + f_ZES * numpy.sin(zdr) + f_ZEC * numpy.cos(zdr)
    return naz, -nzd

