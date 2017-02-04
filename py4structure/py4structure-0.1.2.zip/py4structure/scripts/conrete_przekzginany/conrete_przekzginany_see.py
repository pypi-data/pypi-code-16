from strupy import units as u

#!
'''
##*Obliczenie zbrojenia w przekroju zginanym prostokatnym*

*(metoda maksymalnie uproszczona)*
'''

#! ###1.Wymiary przekroju
h = 1200 *   u.mm  #<< - wysokosc przekoju
b = 400 * u.mm #<< - szerokosc przekroju

#! ###2.Obciazenie
Msd = 1200 *  u.kNm #<< - moment obliczeniowy

#! ###3.Material
materials = [300 * u.MPa, 400 * u.MPa, 500 * u.MPa]
fyd = materials[1] #<< - stal zbrojeniowa

#! ---

#%img conrete_przekzginany_fig1.png

#! Ze wzoru:

As1 = (  Msd / (0.8 * h) * 1 / fyd  ).asUnit(u.mm2) #%requ

#!
'''
---
###Podsumowanie
Dla przekroju o wymiarach val_b x val_h i obciazeniniu var_Msd 
potrzebne zbrojenie dolem var_As1
'''


'''
SeeDescription :
Category - ConcreteStructure

Wylicza zbrojenie zginanego przekroju prostokątnego.
'''