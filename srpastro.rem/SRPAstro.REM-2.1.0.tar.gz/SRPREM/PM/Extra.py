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

History : (28/08/2012) First version.
        : (03/12/2013) Better naming.
        : (07/01/2014) Better organization of parameters.
        : (20/08/2014) Porting to Pilar3.
"""

import numpy
from .Full import Full


def cotg (ang):
    return 1./numpy.tan(ang)


def Extra (xxx_todo_changeme, xxx_todo_changeme1):
    # AAN, ZAN: error in the leveling of the telescope toward north
    # AAE, ZAE: error in the leveling of the telescope toward east
    # NPAE: non-perpendicularity of the azimuth and elevation axis
    # BNP: non-perpendicularity of the optical and the elevation axis
    # AES, AEC, ZES, ZEC:  eccentricity of the encoders
    # AOFF: azimuth zero point correction
    # ZOFF: altitude zero point correction
    # ES2A = C1: Irregularities in the bearing race
    # EC2A = C2: Irregularities in the bearing race
    # C5: Empirical term
    (az,alt) = xxx_todo_changeme
    (e_AAN,e_ZAN,e_AAE,e_ZAE,e_NPAE,e_BNP,e_AES,e_AEC,e_ZES,e_ZEC,e_AOFF,e_ZOFF,e_AS2A,e_AC2A,e_ZS2A,e_ZC2A,e_C5) = xxx_todo_changeme1
    zd = 90.0 - alt
    #
    azr = numpy.radians(az)
    zdr = numpy.radians(zd)
    #
    naz, nalt = Full((az,alt),(e_AAN,e_ZAN,e_AAE,e_ZAE,e_NPAE,e_BNP,e_AES,e_AEC,e_ZES,e_ZEC,e_AOFF,e_ZOFF))
    naz = naz + (e_AS2A * numpy.cos(2*azr) + e_AC2A * numpy.cos(2*azr)) * cotg(zdr)
    nzd = -nalt
    nzd = nzd + e_ZS2A * numpy.sin(2*azr) + e_ZC2A * numpy.cos(2*azr) + e_C5 / numpy.sin(zdr)
    return naz, -nzd

