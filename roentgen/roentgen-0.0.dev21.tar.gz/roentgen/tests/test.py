import roentgen
import astropy.units as u
import roentgen.absorption as abs

#print(abs.is_an_element('Be'))
#print(abs.is_an_element('Gold'))

#print(abs.get_atomic_number("Au"))

all_materials = list(roentgen.elements['symbol']) + list(roentgen.compounds['symbol'])

#abs.Material('Be', 100 * u.m)

print(roentgen.compounds.loc['cdte'])
print(roentgen.elemental_densities[0]['density'])
for mat in all_materials:
    print(mat)
    print(abs.is_an_element(mat))
    print(abs.Material(mat, 100 * u.m).transmission(1 * u.keV))
