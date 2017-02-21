""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.1.1
Author  : Stefano Covino
Date    : 20/08/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (28/08/2013) First version.
        : (03/12/2013) Better naming.
        : (07/01/2014) Better organization of parameters.
        : (20/08/2014) Porting to Pilar3.
"""

from .Extra import Extra
from SRP.SRPMath.FastAngularDistance import FastAngularDistance



def minExtra (xxx_todo_changeme,taz,talt,oaz,oalt):
    (e_AAN,e_ZAN,e_AAE,e_ZAE,e_NPAE,e_BNP,e_AES,e_AEC,e_ZES,e_ZEC,e_AOFF,e_ZOFF,e_AS2A,e_AC2A,e_ZS2A,e_ZC2A,e_C5) = xxx_todo_changeme
    caz, calt = Extra((taz,talt),(e_AAN,e_ZAN,e_AAE,e_ZAE,e_NPAE,e_BNP,e_AES,e_AEC,e_ZES,e_ZEC,e_AOFF,e_ZOFF,e_AS2A,e_AC2A,e_ZS2A,e_ZC2A,e_C5))
    return FastAngularDistance(oaz,oalt,caz,calt).sum()

