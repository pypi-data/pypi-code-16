""" Init file for SRPPolarimetry

Context : SRP
Module  : Polarimetry
Version : 1.4.1
Author  : Stefano Covino
Date    : 17/02/2017
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino

Usage   : to be imported

History : (21/02/2012) First named version.
        : (29/02/2012) Wave plate matrix added.
        : (02/09/2013) ISM matrix added.
        : (16/07/2014) PolBias added.
        : (20/01/2015) Simple transmission matrix added.
        : (22/05/2015) Polarizer matrix added.
        : (17/02/2017) Rayleigh sky model.
"""


__all__ = ['AluminiumRefractiveIndex', 'MuellerISMMatrix','MuellerMetallicMirrorMatrix',
            'MuellerRotationMatrix','MuellerTransmissionMatrix', 'MuellerHalfWavePlateMatrix',
           'MuellerPolarizerMatrix', 'MuellerQuarterWavePlateMatrix', 'MuellerWavePlateMatrix',
           'Pol2Stokes', 'PolBias', 'RayleighSkyModel', 'Stokes2Pol', 'TransmissionMatrix']



