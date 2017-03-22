'''
Tests for beamtools package

Created on Wed Mar 22 17:04:59 2017

@author: cpkmanchee
'''

h = 6.62606957E-34  #J*s
c = 299792458.0     #m/s

def energy(wave):
    return h*c/wave

def freq(wave):
    return c/wave
    