""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.2.1
Author  : Stefano Covino
Date    : 20/08/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (23/08/2012) First version.
        : (01/07/2013) Better check of paramter names.
        : (22/08/2013) Improvement.
        : (03/12/2013) Better naming.
        : (07/01/2014) Better organization of parameters.
        : (20/08/2014) Porting to Pilar3.
"""

from .Full import Full
from SRP.SRPMath.FastAngularDistance import FastAngularDistance



def minFull (xxx_todo_changeme,taz,talt,oaz,oalt):
    (f_AAN,f_ZAN,f_AAE,f_ZAE,f_NPAE,f_BNP,f_AES,f_AEC,f_ZES,f_ZEC,f_AOFF,f_ZOFF) = xxx_todo_changeme
    caz, calt = Full((taz,talt),(f_AAN,f_ZAN,f_AAE,f_ZAE,f_NPAE,f_BNP,f_AES,f_AEC,f_ZES,f_ZEC,f_AOFF,f_ZOFF))
    return FastAngularDistance(oaz,oalt,caz,calt).sum()

