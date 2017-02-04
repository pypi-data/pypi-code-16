# -*- coding: utf-8 -*-

#! ###*Nosność polączenia śrubowego wg PN-90 / B-3200*

import strupy.units as u

#from strupy.steel.BoltConnect_PN import BoltConnect_PN
from BoltConnect_PN import BoltConnect_PN

BoltConnect = BoltConnect_PN() # Bolt_PN.py BoltConnect_PN.py


#! ###* 1. Dane sruby *
dimlist = BoltConnect.get_AvailableBoltDim()
dim = dimlist [3] #<<<< Wielkosc sruby -
BoltConnect.set_BoltDim(dim)

gradelist = BoltConnect.get_AvailableBoltGrade()
grade = gradelist [8] #<<<< Klasa sruby -
BoltConnect.set_BoltGrade(grade)

#! ###* 2. Dane blach *
tlist = [6*u.mm, 8*u.mm, 10*u.mm, 12*u.mm, 14*u.mm, 16*u.mm, 18*u.mm, 20*u.mm, 22*u.mm, 24*u.mm,  26*u.mm, 28*u.mm]
t = tlist [2] #<<<< Minimalna suma grubosci blach dla kierunku - 
BoltConnect.t1 = t
BoltConnect.t2 = t

mlist = [1, 2, 3, 4]
m = mlist[0] #<<<< Ilosc plaszczyzn ciecia sruby - 
m = m * 1.0
BoltConnect.m = m

fdlist = ['St0', 175*u.MPa, 165*u.MPa,'St3' ,215*u.MPa, 205*u.MPa, 195*u.MPa, 'St4', 235*u.MPa, 225*u.MPa, '18G2', 305*u.MPa, 295*u.MPa, 285*u.MPa]
fd = fdlist[11] #<<<< Wytrzymalosc obliczeniowa stali blach - 
BoltConnect.fd = fd

mi = 0.2 #<<<< Wspolczynnik tarcia -
BoltConnect.mi = mi

#! ###* 3. Rozstaw srub w polaczeniu *
a1min = 1.5 * BoltConnect.d
a1 = 40 * u.mm  #<<<< Odleglosc sruby od czola blachy (a1 - min 1.5d = %(a1min)s) - 
BoltConnect.a1 = a1

amin = 2.5 * BoltConnect.d
a = 50 * u.mm   #<<<< Rozstaw srub (a - min 2.5d = %(amin)s) - 
BoltConnect.a = a

# ---------calculating--------------------------
BoltConnect._calculateconnect()
# -----------------------------------

#!-----------------------------------

#! ###*4.Wyniki*


#! ###Nosnosci podlozna zlacza

#%img steel_nosnosc_srub_fig1.png

#! *Polaczenie doczlowe zwykle*
SRt = BoltConnect.SRt.asUnit(u.kN) #! - zerwanie trzpienia
# Obliczenie minimalnej grubosc blachy
d = BoltConnect.d
c = d
bs = 2*c + d
tmin = 1.2 * (c * SRt / (bs * fd))**0.5
tmin = tmin.asUnit(u.mm)#! - minimalna grubosc blachy w polaczeniu doczolowym zwyklym (wg (82) pkt 6.2.4.3 PN) - dla c = %(c)s, bs = %(bs)s)
tmin = tmin * 1.62 #! - w przypadku obciazen dynamicznych

#! *Polaczenie doczlowe sprezone*
SRr = BoltConnect.SRr.asUnit(u.kN) #! - rozwarcie styku obc statycznie jesli sruba sprezona
SRrdyn = BoltConnect.SRrdyn.asUnit(u.kN) #! - rozwarcie styku obc dynamicznie jesli sruba sprezona
# Obliczenie minimalnej grubosc blachy
Rm = BoltConnect.Rm
tmin = d * ( Rm.asUnit(u.MPa).asNumber() / 1000.0 )**(1.0/3.0)
tmin = tmin.asUnit(u.mm)#! - minimalna grubosc blachy w polaczeniu doczolowym sprezonym obc statycznie (wg (83) pkt 6.2.4.3 PN) - dla c = %(c)s, bs = %(bs)s)
tmin = tmin * 1.25 #! - w przypadku obciazen dynamicznych


#!-----------------------------------
#! ###Nosnosci poprzeczna zlacza (dla m = %(m)s ciec)
#%img nosnosc_srub_fig2.png
SRv = BoltConnect.SRv.asUnit(u.kN) #! - sciecie trzpienia
SRb = BoltConnect.SRb.asUnit(u.kN) #! - uplastycznienie wskutek docisku do scianek otworu (Et = %(t)s)
SR = min (SRv, SRb)
#! ####[Nosnosc w polaczeniu zakladkowym zwyklym  Min(SRv, SRb) - %(SR)s]
SRs = BoltConnect.SRs.asUnit(u.kN) #! - poslizg stylu jesli sruba sprezona (wsp. tarcia %(mi)s)

'''
SeeDescription :
Category - SteelStructure

Obliczanie nosność śrub.
'''




