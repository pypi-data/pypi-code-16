#! /usr/bin/env python

"""Check energies against the databases published in
   Brenner et al., J. Phys. Condens. Matter 14, 783 (2002)
   Schall, Harrison (2012)
"""

from __future__ import print_function

import os
import sys

import numpy as np

import ase
import ase.io
import ase.optimize

import atomistica

###

ETOL = 0.005

refdb = '/home/pas/Data/structure_database'

###

def PBE_cohesive_energy(mol):
    eat = {}
    for el in set(mol.get_chemical_symbols()):
        e = np.loadtxt('{}/atoms/{}/GPAW_PBE/e.out'.format(refdb, el))
        eat[el] = np.min(e)
    hill = mol.get_chemical_formula('hill')
    e = 0.0
    for fn in ['e.out', 'potential_energy__magmom0.out',
               'potential_energy__magmom1.out',
               'potential_energy__magmom2.out']:
        fullfn = '{0}/molecules/{1}/GPAW_PBE/{2}'.format(refdb, hill, fn)
        if os.path.exists(fullfn):
            e = min(e, np.min(np.loadtxt(fullfn)))
    for el in mol.get_chemical_symbols():
        e -= eat[el]
    return e

###

sys.path += ['.']
from database import (molecule, reference_database, Brenner_et_al_CH,
                      Schall_Harrison_SiH, Schall_Harrison_CSiH,
                      find_molecule)

###

def optimize_molecule(mol, c):
    a = molecule(mol)
    a.center(vacuum=5.0)

    a.set_calculator(c)
    #a.rattle(0.05)
    #ase.optimize.QuasiNewton(a, logfile='QuasiNewton.log') \
    #    .run(fmax=0.001)
    ase.optimize.FIRE(a, logfile='FIRE.log').run(fmax=0.001)
    return a

###

if __name__ == '__main__':

    if len(sys.argv) == 2:
        mol = sys.argv[1]
        ecbsqb3, de = find_molecule(mol)
        eref = ecbsqb3-de

        c = atomistica.Rebo2SiCH(introspection=True)

        a = optimize_molecule(mol, c)
        ase.io.write('opt.xyz', a)
        e = a.get_potential_energy()

        #epbe = PBE_cohesive_energy(a)
        epbe = 0

        print('{0:>20} {1:>20} {2:>20} {3:>20} {4:>20}' \
            .format('name', 'energy', 'CBS-QB3', 'difference', 'DFT-PBE'))
        print('{0:>20} {1:>20} {2:>20} {3:>20} {4:>20}' \
            .format('====', '======', '=========', '==========', '=========='))
        print('{0:>20} {1:>20.10f} {2:>20.10f} {3:>20.10f} {3:>20.10f}' \
            .format(mol, e, eref, e-eref, epbe))
        print()

        i, j, abs_dr = c.nl.get_neighbors(c.particles)
        syms = a.get_chemical_symbols()
        print('{:>9} {:>9} {:>12} {:>12} {:>12} {:>12} {:>12} {:>12} {:>12} {:>12}' \
            .format('i', 'j', 'Fij', 'Pij', 'Pji', 'bij', 'bji', 'baveij', 'VA', 'VR'))
        print('{:>9} {:>9} {:>12} {:>12} {:>12} {:>12} {:>12} {:>12} {:>12} {:>12}' \
            .format('---', '---', '---', '---', '---', '---', '---', '------', '---', '---'))
        for _i, _j, _Fij, _Pij, _Pji, _bij, _bji, _baveij, _VA, _VR in \
            zip(i, j, c.pots[0].Fij, c.pots[0].Pij, c.pots[0].Pji,
                c.pots[0].bij, c.pots[0].bji, c.pots[0].baveij, c.pots[0].VA,
                c.pots[0].VR):
            if abs(_baveij) > 0.0:
                print('{:3} ({:3}) {:3} ({:3}) {:12.8} {:12.8} {:12.8} {:12.8} {:12.8} {:12.8} {:12.8} {:12.8}' \
                    .format(_i, syms[_i], _j, syms[_j], _Fij, _Pij, _Pji, _bij, _bji, _baveij, _VA, _VR))
    else:
        for potname, c, reference_database in [ 
            #( 'Rebo2', atomistica.Rebo2(),
            #  Brenner_et_al_CH ),
            ( 'Rebo2SiCH', atomistica.Rebo2SiCH(),
              Brenner_et_al_CH+Schall_Harrison_SiH+Schall_Harrison_CSiH ),
            #( 'Rebo2SiCHScr', atomistica.Rebo2SiCHScr(),
            #  Brenner_et_al_CH+Schall_Harrison_SiH+Schall_Harrison_CSiH )
            ]:
    
            print('=== Testing {0} ==='.format(potname))
    
            nok = 0
            nfailed = 0
        
            for mol, ecbsqb3, de in reference_database:
                if len(sys.argv) > 1:
                    if mol not in sys.argv[1:]:
                        continue
    
                eref = ecbsqb3-de

                a = optimize_molecule(mol, c)    
                e = a.get_potential_energy()

                #epbe = PBE_cohesive_energy(a)
                epbe = 0
    
                if abs(e-eref) > ETOL:
                    print('{0:>20} {1:>20.10f} {2:>20.10f} {3:>20.10f} - {4:>20.10f} {5:>20.10f} {6:>20.10f}      ' \
                        '.failed.'.format(mol, e, eref, e-eref, ecbsqb3, epbe, ecbsqb3-epbe))
                    nfailed += 1
                else:
                    print('{0:>20} {1:>20.10f} {2:>20.10f} {3:>20.10f} - {4:>20.10f} {5:>20.10f} {6:>20.10f}  .ok.' \
                        .format(mol, e, eref, e-eref, ecbsqb3, epbe, ecbsqb3-epbe))
                    nok += 1
    
            print('{0} molecule tests ok, {1} molecule tests failed.' \
                .format(nok, nfailed))
    
