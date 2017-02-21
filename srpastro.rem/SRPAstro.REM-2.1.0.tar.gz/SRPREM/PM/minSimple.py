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

History : (23/08/2012) First version.
        : (22/08/2013) Improvement.
        : (20/08/2014) Porting to Pilar3.
"""


from .Simple import Simple
from SRP.SRPMath.FastAngularDistance import FastAngularDistance


def minSimple (xxx_todo_changeme,taz,talt,oaz,oalt):
    (s_AOFF,s_ZOFF) = xxx_todo_changeme
    caz, calt = Simple((taz,talt),(s_AOFF,s_ZOFF))
    return FastAngularDistance(oaz,oalt,caz,calt).sum()
