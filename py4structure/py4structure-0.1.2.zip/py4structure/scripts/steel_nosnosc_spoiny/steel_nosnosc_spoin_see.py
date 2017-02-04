# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------------------
#! ##*Nosnosc spoin pachwinowych dfdf dfdf wg PN-90 / B-3200*

import strupy.units as u

fdlist = ['St0', 175*u.MPa, 165*u.MPa,'St3' ,215*u.MPa, 205*u.MPa, 195*u.MPa, 'St4', 235*u.MPa, 225*u.MPa, '18G2', 305*u.MPa, 295*u.MPa, 285*u.MPa]
fd = fdlist[11] #<< - wytrzymalosc obliczeniowa stali blach - 
Re = 1.1 * fd #! - granica plastycznosci

#! ------------------------------------------------------------------------------

#! ##*1.Polaczenie zakladkowe*

tlist = [4*u.mm, 6*u.mm, 8*u.mm, 10*u.mm, 12*u.mm, 14*u.mm, 16*u.mm, 18*u.mm, 20*u.mm, 22*u.mm, 24*u.mm,  26*u.mm, 28*u.mm]
ta = tlist [2] #<< - grubosc blachy a
tb = tlist [2] #<< - grubosc blachy b

t1 = min(ta, tb) #! - grubosc ciebszej blachy
t2 = max(ta, tb) #! - grubosc grubszej blachy

tmin = max( min(0.2*t2, 10*u.mm), 2.5*u.mm) #! - minimalna grubosc
tmax = min(0.7 * t1, 16*u.mm) #%requ - maksymalna grubosc

alist = [2.5*u.mm, 3*u.mm, 4*u.mm, 5*u.mm, 6*u.mm, 8*u.mm, 10*u.mm, 12*u.mm, 14*u.mm, 16*u.mm]
a = alist [2] #<< - grubosc spiny - ma byc w granicy %(tmin)s - %(tmax)s

t_alert = ''
if tmin > a:
    t_alert = '!!!Grubosc spoiny zbyt mala!!!'
if a > tmax:
    t_alert = '!!!Grubosc spoiny zbyt duza!!!'

#! ### %(t_alert)s

lmin = 10 * a #%requ - dlugosc minimalna spoiny
lmax = 100 * a #%requ - dlugosc mmaksymalna spoiny

#! ------------------------------------------------------------------------------

#! ### *Nosnosc przy obciazeniu osiowym sila N*
#%img steel_nosnosc_spoin_fig1.png
l = 160 * u.mm  #<< - dlugosc spiny, ma byc w granicy %(lmin)s - %(lmax)s
if l > 100 * a :
    l = lmax
    #! ####Spoina zbyt dluga -  do obliczen przyjeto - var_l
if l < 10 * a :
    l = 0 * u.mm
    #! ####Spoina zbyt krotka -  do obliczen przyjeto - var_l
nlist = [1, 2, 3, 4]
n = nlist[1] #<< - ilosc spoin o dlugosci l jw.
sum_l = n * l #! - laczna dlugosc spoin
alfa_II = 0
if (Re <= 255*u.MPa):
    alfa_II = 0.8
if (255*u.MPa < Re <= 355*u.MPa):
    alfa_II = 0.7
if (255*u.MPa < Re <= 255*u.MPa):
    alfa_II = 0.7

alfa_II #! - wspolczynnik wytrzymalosci spoiny

Nrd = a * sum_l * fd * alfa_II #equ
Nrd = Nrd.asUnit(u.kN) 
#! Nosnosc spoin na sile podluzna rownolegla do spoin:
#! #### *Nrd = %(Nrd)s*

bmax = min(l, 30*t1)
#! Odleglosc skrajnych spoin nie wieksza niz min(l, 30xt1) = min(%(l)s, 30x%(t1)s) = %(bmax)s


'''
SeeDescription : 
Category - SteelStructure

Obliczanie nosność spoiny pachwinowej.
'''