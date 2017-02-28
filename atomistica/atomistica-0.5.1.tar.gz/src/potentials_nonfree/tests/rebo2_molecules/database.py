#! /usr/bin/env python

import os

import ase.io
import ase.structure

# molecule, atomization energy (eV), zero-point energy (kcal mol^-1), dHpot (kcal mol^-1)

# C, H --- Brenner et al., Table 12
Brenner_et_al_CH = [
    ( 'CH2_s1A1d',            -8.4693,   0.000 ),
    ( 'CH3',                 -13.3750,   0.000 ),
    ( 'CH4',                 -18.1851,   0.000 ), # methane
    ( 'C2H',                 -11.5722,   0.000 ),
    ( 'C2H2',                -17.5651,   0.000 ), # acetylene
    ( 'C2H4',                -24.5284,   0.000 ), # ethylene
    ( 'H3C2H2',              -26.5879,   0.000 ),
    ( 'C2H6',                -30.8457,   0.000 ), # ethane
    ( 'C3H4_C2v',            -28.3610,   0.000 ), # cyclopropene
    ( 'CH2=C=CH2',           -30.3511,   0.000 ),
    ( 'propyne',             -30.3076,   0.000 ),
    ( 'C3H6_D3h',            -36.8887,   0.000 ), # cyclopropane
    ( 'C3H6_Cs',             -37.5116,   0.000 ), # propene
    ( 'C3H8',                -43.5891,   0.000 ), # propane
    ( 'cyclobutene',         -42.1297,   0.000 ),
    ( 'butadiene',           -43.3977,   0.000 ),
    ( 'CH3CH=C=CH2',         -43.3320,   0.000 ),
    ( '1-butyne',            -43.0510,   0.000 ),
    ( '2-butyne',            -43.0501,   0.000 ),
    ( 'cyclobutane',         -49.8986,   0.000 ), # this one fails. Ref energy from paper is -49.7126
    ( '1-butene',            -50.2557,   0.000 ),
    ( 'cis-butene',          -50.4951,   0.000 ),
    ( 'i-C4H9',              -52.0728,   0.000 ),
    ( 't-C4H9',              -52.6588,   0.000 ),
    ( 'trans-butane',        -56.3325,   0.000 ), # n-butane
    ( 'isobutane',           -56.3307,   0.000 ),
    ( '1,3-pentadiene',      -56.3731,   0.000 ),
    ( '1,4-pentadiene',      -56.9219,   0.000 ),
    ( 'cyclopentene',        -57.3895,   0.000 ),
    ( '1,2-pentadiene',      -56.0761,   0.000 ),
    ( '2,3-pentadiene',      -56.3130,   0.000 ),
    ( 'cyclopentane',        -63.6453,   0.000 ),
    ( '2-pentene',           -63.2391,   0.000 ),
    ( '1-butene,2-methyl',   -63.4147,   0.000 ),
    ( '2-butene,2-methyl',   -63.6546,   0.000 ),
    ( 'n-pentane',           -69.0760,   0.000 ),
    ( 'isopentane',          -69.0741,   0.000 ),
    ( 'neopentane',          -69.0614,   0.000 ),
    ( 'C6H6',                -60.2313,   0.000 ), # benzene
    ( 'cyclohexane',         -76.4605,   0.000 ),
    ( 'naphthalene',         -95.9448,   0.000 ),
    ]

# Si, H --- Schall, Harrison, Table 8
Schall_Harrison_SiH = [
    ( 'SiH',                   -3.070,   0.000 ),
    ( 'SiH2',                  -6.375,   0.000 ),
    ( 'SiH3',                  -9.311,  -0.048 ),
    ( 'SiH4',                 -13.256,   0.000 ),
    ( 'Si2H',                  -6.017,   0.000 ),
    ( 'SiSiH2',                -9.178,   0.000 ),
    ( 'Si2H2',                 -8.073,   0.000 ),
    ( 'SiSiH3',               -12.474,  -0.128 ),
    ( 'SiH2SiH',              -11.829,   0.000 ),
    ( 'Si2H4',                -15.330,   0.000 ),
    ( 'Si2H5',                -18.040,  -0.129 ),
    ( 'Si2H6',                -21.856,   0.000 ),
    ( 'Si3',                   -6.833,   0.000 ),
    ( 'SiSiH(SiH2)',          -15.354,  -0.867 ),
    ( 'SiH2=Si=SiH2',         -18.300,   0.335 ),
    ( 'SiH3SiSiH',            -17.308,  -0.091 ),
    ( 'Si3H5',                -20.598,   0.062 ),
    ( 'SiH2=SiHSiH3',         -23.062,   1.105 ),
    ( 'n-Si3H7',              -26.762,  -0.113 ),
    ( 'i-Si3H7',              -26.853,   0.237 ),
    ( 'Si3H8',                -30.553,   0.000 ),
    ( 'Si4',                   -8.698,   0.000 ),
    ( 'SiSiH=SiHSi',          -14.397,   0.097 ),
    ( 'c-Si4H4',              -22.180,  -0.462 ),
    ( 'SiH2=(SiH)2=SiH2',     -26.577,  -0.181 ),
    ( 'c-Si4H8',              -34.175,   0.085 ),
    ( 'n-Si4H9',              -35.482,  -0.135 ),
    ( '2-Si4H9',              -35.566,   0.266 ),
    ( '1i-Si4H9',             -35.551,  -0.073 ),
    ( 'i-Si4H9',              -35.738,   0.683 ),
    ( 'Si4H10',               -39.265,  -0.015 ),
    ( 'i-Si4H10',             -39.339,   0.000 ),
    ( 'SiH3SiH=SiHSiH3',      -33.028,   0.000 ),
    ( '(SiH3)2Si=SiH2',       -33.111,   0.057 ),
    ( 'n-Si5H12',             -47.981,  -0.035 ),
    ( 'c-Si5H10',             -43.344,   0.126 ),
    ( 'i-Si5H12',             -48.067,  -0.031 ),
    ( 'Si5H12',               -48.222,   0.114 ),
    ( 'Si6H5',                -30.888,   0.000 ),
    ( 'Si6H6',                -34.386,   0.000 ),
    ( '(SiH3)2Si=Si(SiH3)2',  -50.866,   0.180 ),
    ( 'c-Si6H12',             -52.226,  -0.044 ),
    ( 'Si6H14',               -56.699,  -0.055 ),
    ]

# C, Si, H --- Schall, Harrison, Table 9
Schall_Harrison_CSiH = [
    ( '(CH3)2Si=CH2',         -43.717,   0.007 ),
    ( '(CH3)3CSiH3',          -61.535,   0.000 ),  # okay
    ( '(CH3)3SiSiH3',         -59.061,  -0.197 ),
    ( '(CH3)4Si',             -62.884,  -0.510 ),
    ( '(SiH3)2C=CH2',         -40.459,   0.000 ),
    ( '(SiH3)2CH2',           -34.338,   0.000 ),  # -0.025
    ( '(SiH3)2CH3CCH3',       -58.184,   0.000 ),  # -0.011
    ( '(SiH3)2CHCH3',         -46.203,   0.000 ),  # -0.015
    ( '(SiH3)2Si(CH3)2',      -55.321,   0.034 ),
    ( '(SiH3)2SiHCH3',        -42.914,   0.164 ),
    ( 'CH(SiH3)3',            -43.190,   0.493 ),  # 0.389
    ( 'CH2=Si(SiH3)2',        -36.443,  -0.032 ),
    ( 'CH2SiCH2',             -24.237,  -1.057 ),
    ( 'CH3C(SiH3)3',          -55.055,   0.000 ),
    ( 'CH3Si==SiH',           -20.435,  -0.165 ),
    ( 'CH3SiH2CH3',           -38.005,   0.001 ),
    ( 'CH3SiH3CHCH3',         -49.458,   0.001 ),
    ( 'CH3SiH3Si=CH2',        -40.054,   0.014 ),
    ( 'CH3SiH=CH2',           -31.306,   0.110 ),
    ( 'SiH(CH3)3',            -50.431,  -0.334 ),
    ( 'SiH2=C=SiH2',          -21.161,   0.880 ),
    ( 'SiH2=CHSiH3',          -27.807,   0.219 ),
    ( 'SiH2C(SiH3)2',         -36.932,   0.048 ),
    ( 'SiH2CH2',              -18.942,   0.001 ),
    ( 'SiH3C==CH',            -25.858,  -1.114 ), # this one fails - Ref. from paper is 0.035
    ( 'SiH3CH2CH3',           -37.471,   0.000 ),
    ( 'SiH3CH3',              -25.610,   0.000 ),
    ( 'SiH3CH3C=CSiH3CH3',    -64.522,   0.000 ),
    ( 'SiH3SiH(CH3)2',        -46.623,  -0.036 ),
    ( 'SiH3SiH2CH3',          -34.218,   0.000 ),
    ( 'SiH3SiH=CH2',          -27.648,   0.111 ),
    ( 'SiH==CH',              -11.351,  -0.685 ),  # 0.000
    ( 'CCSi',                 -12.599,  -2.279 ),  # fails - Table 9 was -0.993. Dave say -1.480
    ( 'CH2CH2SiH3',           -33.232,  -0.099 ),
    ( 'CH2Si',                -13.157,   0.000 ),
    ( 'CH2SiH3',              -21.259,   0.547 ),
    ( 'CH3CH2Si',             -27.362,  -0.774 ),
    ( 'CH3CH2SiH',            -30.606,  -0.213 ),
    ( 'CH3CH2SiH2',           -33.500,   0.182 ),
    ( 'CH3CHSiH3',            -33.313,   0.859 ),
    ( 'CH3SiH',               -18.751,  -0.255 ),
    ( 'CH3SiH2',              -21.630,   0.187 ),
    ( 'CH3SiH2Si',            -24.132,   0.598 ),
    ( 'CH3SiH2SiH',           -27.361,   0.473 ),
    ( 'CH3SiH2SiH2',          -30.417,  -0.137 ),
    ( 'CH3SiHCH3',            -33.989,   0.493 ),
    ( 'CH3SiHSiH3',           -30.366,   0.593 ),
    ( 'CHCH2SiH3',            -31.732,   0.000 ),
    ( 'CHSiH2',               -14.337,   0.049 ), # -0.057 in paper
    ( 'CHSiH2SiH3',           -27.884,   0.142 ),
    ( 'CHSiH3',               -16.815,   0.379 ),
    ( 'CHSi',                  -8.998,  -0.799 ),
    ( 'CSiC',                  -7.188,   0.900 ),
    ( 'CSiH',                  -6.324,   0.776 ),
    ( 'CSiH2SiH3',            -23.442,   0.061 ), # -0.071 in paper
    ( 'CSiH3',                -12.166,   0.331 ),
    ( 'CSiSi',                 -7.086,   1.270 ),
    ( 'CSi',                   -4.388,   0.000 ),
    ( 'SiCSi',                -10.924,  -0.766 ),
    ( 'SiH3CHSiH3',           -30.086,   0.699 ),
    ( 'SiH2(CH3)2',           -38.005,   0.000 ),
    #( 'SiH3-CH2-SiH3',         0.000,    0.000 ),
    #( 'CH2SiH',                0.000,    0.000 ),
    ]

reference_database = \
    Brenner_et_al_CH + \
    Schall_Harrison_SiH + \
    Schall_Harrison_CSiH

def find_molecule(refmol):
    for mol, edft, de in reference_database:
        if mol == refmol:
            return edft, de
    raise RuntimeError("Molecule '{}' not found in database.".format(refmol))

def read_coord(fn):
    r = [ ]
    num = [ ]
    f = open(fn)
    nat = int(f.readline())
    f.readline()
    for i in range(nat):
        dummy1, inum, dummy2, ix, iy, iz = f.readline().split()
        num += [ inum ]
        r += [ ( ix, iy, iz ) ]
    return ase.Atoms(numbers=num, positions=r)

def molecule(mol):
    if os.path.exists('{0}.coord'.format(mol)):
        a = read_coord('{0}.coord'.format(mol))
    elif os.path.exists('{0}.xyz'.format(mol)):
        a = ase.io.read('{0}.xyz'.format(mol))
    else:
        a = ase.structure.molecule(mol)
    a.set_pbc(False)
    return a
