from __future__ import print_function
"""Utilities for converting MATCH SFH for use in TRILEGAL."""
import argparse
import numpy as np
import sys
import os

def read_binned_sfh(filename):
    '''
    read the MATCH calcsfh, zcombine, or hybridMC output file as recarray.

    NOTE:
    This code calls genfromtext up to 3 times. There may be a better way to
    figure out how many background lines or if there is a header.
    It's a small file so it's not a big deal.
    '''
    dtype = [('lagei', '<f8'),
             ('lagef', '<f8'),
             ('dmod', '<f8'),
             ('sfr', '<f8'),
             ('sfr_errp', '<f8'),
             ('sfr_errm', '<f8'),
             ('mh', '<f8'),
             ('mh_errp', '<f8'),
             ('mh_errm', '<f8'),
             ('mh_disp', '<f8'),
             ('mh_disp_errp', '<f8'),
             ('mh_disp_errm', '<f8'),
             ('csfr', '<f8'),
             ('csfr_errp', '<f8'),
             ('csfr_errm', '<f8')]
    try:
        data = np.genfromtxt(filename, dtype=dtype)
    except ValueError:
        try:
            data = np.genfromtxt(filename, dtype=dtype, skip_header=6,
                                 skip_footer=1)
        except ValueError:
            data = np.genfromtxt(filename, dtype=dtype, skip_header=6,
                                 skip_footer=2)
    return data.view(np.recarray)


def read_popbox(filename):
    """
    Parse MATCH's popbox file

    Parameters
    ----------
    filename : str
        population box file

    Returns
    -------
    sets as attributes:
        mh : array
            metalicity (line 2 of popbox file)
        lagei : array
            log age bin 0 (first column after line 2)
        lagef : array
            log age bin 1 (second column after line 2)
        sfr : array
            star formation rate grid shape Nages x Nmhs
    """
    with open(filename) as inp:
        lines = [np.float_(next(inp).strip().split()) for l in range(2)]

    mh = lines[1]
    data = np.genfromtxt(filename, skip_header=2)
    lagei = data.T[0]
    lagef = data.T[1]
    sfr =  data.T[2:].T
    return lagei, lagef, mh, sfr


def process_match_popbox(popbox, outfile=None, zsun=0.01524, zdisp=None):
    """
    Convert a population box to trilegal AMR input file
    Parameters
    ----------
    outfile : str
        file to save to default: add .trisfh to filename
    zsun : float
        solar metallicity
        this file should match the value in MATCH/PARSEC/makemod.cpp
        for Padua, use 0.02 for PARSEC, use 0.01524
    zdisp : float or array
        add zdispersion as a column

    Returns
    -------
        outfile : str
            trilegal AMR file (also saves it to disk)
    """
    lagei, lagef, mh, sfr = read_popbox(popbox)

    if outfile is None:
        outfile = '{0:s}.trisfh'.format(popbox)

    zdisp = zdisp or ''
    zdisp = np.atleast_1d(zdisp)
    if len(zdisp) == 1:
        zdisp = np.repeat(zdisp, len(mh))

    if len(zdisp) != len(mh):
        print('Error: z dispersion must be one value or an array length {0:d}'.format(len(mh)))
        sys.exit(1)

    fmt = '{0:7.4f} {1:7.6e} {2:7.6f} {3!s} \n'
    frac = np.min(np.diff(lagei)) * .1

    sfr *= 1e3  # sfr is normalized in trilegal so units is 1e-3 Msun/yr
    z = zsun * 10 ** (mh)
    lines = ''
    for j in range(len(lagei)):
        for i in range(len(mh)):
            if sfr[j, i] == 0:
                continue
            lines += fmt.format(lagei[j], 0.0, z[i], zdisp[i])
            lines += fmt.format(lagei[j] + frac, sfr[j, i], z[i], zdisp[i])
            lines += fmt.format(lagef[j], sfr[j, i], z[i], zdisp[i])
            lines += fmt.format(lagef[j] + frac, 0.0, z[i], zdisp[i])

    with open(outfile, 'w') as outp:
        outp.write(lines)

    return outfile


def process_match_sfh(sfhfile, outfile='processed_sfh.out', zdisp=None,
                      zsun=0.01524):
    '''
    Convert a match sfh file into a sfr-z table for trilegal

    Parameters
    ----------
    sfhfile : str
        MATCH sfh file

    outfile : str
        TRILEGAL sfr-z table filename to write to

    zdisp : bool
        Use z-dispersion reported by MATCH

    '''
    # trilegal line format (z-dispersion is a string so it can be empty if 0.)
    fmt = '{:.6g} {:.6g} {:.4g} {} \n'

    data = read_binned_sfh(sfhfile)
    sfr = data['sfr']
    # Trilegal only needs populated time bins, not fixed age array
    inds, = np.nonzero(sfr > 0)
    sfr = sfr[inds]
    to = data['lagei'][inds]
    tf = data['lagef'][inds]
    dlogz = data['mh'][inds]
    half_bin = np.diff(dlogz[0: 2])[0] / 2.

    zdisp = zdisp or ''
    zdisp = np.atleast_1d(zdisp)
    if len(zdisp) == 1:
        zdisp = np.repeat(zdisp, len(dlogz))

    if len(zdisp) != len(dlogz):
        print('Error: z dispersion must be one value or an array length {0:d}'.format(len(mh)))
        sys.exit(1)


    with open(outfile, 'w') as out:
        for i in range(len(to)):
            sfr[i] *= 1e3  # sfr is normalized in trilegal

            # MATCH conversion
            z1 = zsun * 10 ** (dlogz[i] - half_bin)
            z2 = zsun * 10 ** (dlogz[i] + half_bin)

            age1a = 1.0 * 10 ** to[i]
            age1p = 1.0 * 10 ** (to[i] + 0.0001)
            age2a = 1.0 * 10 ** tf[i]
            age2p = 1.0 * 10 ** (tf[i] + 0.0001)

            out.write(fmt.format(age1a, 0.0, z1, zdisp[i]))
            out.write(fmt.format(age1p, sfr[i], z1, zdisp[i]))
            out.write(fmt.format(age2a, sfr[i], z2, zdisp[i]))
            out.write(fmt.format(age2p, 0.0, z2, zdisp[i]))
            out.write(fmt.format(age1a, 0.0, z2, zdisp[i]))
            out.write(fmt.format(age1p, sfr[i], z2, zdisp[i]))
            out.write(fmt.format(age2a, sfr[i], z1, zdisp[i]))
            out.write(fmt.format(age2p, 0.0, z1, zdisp[i]))

    print('wrote {}'.format(outfile))
    return outfile
