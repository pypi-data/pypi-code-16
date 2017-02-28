#! /usr/bin/env python3

# Insert missing molecules into structure database

from __future__ import print_function

import os
import sys
import yaml
from collections import defaultdict

import ase
import ase.io as io

import pybel

sys.path += ['.']
from database import molecule, reference_database, Brenner_et_al_CH

###

def hasupper(s):
    for c in s:
        if c.isupper():
            return True
    return False

###

#root = '/home/pas/Data/structure_database/molecules'
root = 'hydrocarbons'
for mol, e1, e2 in Brenner_et_al_CH:
    a = molecule(mol)
    io.write('{}/{}.xyz'.format(root, mol), a)
    io.write('{}/{}.coord'.format(root, mol), a, format='gaussian')

sys.exit(1)


molecules_by_hill = defaultdict(list)
for mol, e1, e2 in reference_database:
    a = molecule(mol)
    hill = a.get_chemical_formula('hill')

    molecules_by_hill[hill] += [mol]

print(molecules_by_hill)

for hill in molecules_by_hill.keys():
    mols = molecules_by_hill[hill]

    for mol in mols:
        a = molecule(mol)

        defdict = {}
        if hasupper(mol):
            defdict['Formula'] = mol
        else:
            defdict['Name'] = mol
    
        io.write('tmp.xyz', a)
        babelmol = pybel.readfile('xyz', 'tmp.xyz').next()
        smiles = babelmol.write('smi').split('\t')[0]
        defdict['SMILES'] = smiles
    
        #io.write('{}.xyz'.format(smiles), a)

        molroot = '{}/{}'.format(root, hill)
        if not os.path.exists(molroot):
            print('New hill: {}'.format(hill))
            os.mkdir(molroot)

        if len(mols) > 1:
            if os.path.exists('{}/definition.yml'.format(molroot)):
                print('definition.yml in {}, but more than one mol found with this stoichiometry'.format(molroot))
            else:
                molroot = '{}/{}'.format(molroot, smiles.replace('/', '_slash_').replace('\\', '_backslash_'))
                if not os.path.exists(molroot):
                    print('New SMILES: {} ({})'.format(smiles, mol))
                    os.mkdir(molroot)

            deffn = '{}/definition.yml'.format(molroot)
            if not os.path.exists(deffn):
                yaml.dump(defdict, stream=open(deffn, 'w'), default_flow_style=False)
            xyzfn = '{}/prototype.xyz'.format(molroot)
            if not os.path.exists(xyzfn):
                io.write(xyzfn, a)

            gpawroot = '{}/GPAW_PBE'.format(molroot)
            if not os.path.exists(gpawroot):
                os.mkdir(gpawroot)
