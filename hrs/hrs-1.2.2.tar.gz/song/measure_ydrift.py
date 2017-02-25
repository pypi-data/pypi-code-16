#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 23:10:05 2016

@author: cham
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 17:37:24 2016

@author: cham
"""

#%%
import os
import sys
import re
import numpy as np
import ccdproc

from collections import OrderedDict
from astropy.table import Table, Column, Row
from hrs.logtable import log2table
from hrs.aperture import find_apertures, combine_apertures, group_apertures, extract_1dspec, combine_flat, substract_scattered_light
from hrs.calibration import fix_thar_sat_neg, thar_corr2d, interpolate_wavelength_shift, interpolate_order_shift, load_thar_temp
import hrs
#from hrs import *
import hrs
reload(hrs)
from joblib import Parallel, delayed


from scipy.interpolate import interp1d
from skimage.filters import gaussian

import glob
from astropy.io import fits

#%matplotlib qt
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'font.size':20})

from tqdm import tqdm,trange

#%%

day = 20161118
print(day)
os.chdir('/hydrogen/song/star_spec/%s/night/raw/' % day)

#%%


    

fps_all = glob.glob('./*.fits')
fps_all.sort()
t = scan_fits_header(fps_all)

t.add_column(Column(np.zeros((len(t),), dtype=int)*np.nan, 'xdrift'))
t.add_column(Column(np.zeros((len(t),), dtype=bool), 'astemplate'))
#t.show_in_browser()

#%%

""" check Y shift """
ind_bias = t['IMAGETYP'] == 'BIAS'
print("%s BIAS found" % np.sum(ind_bias))
#bias = ccdproc.combine(','.join(t['fps'][ind_bias]), unit='adu', method='average')

ind_flat = t['IMAGETYP'] == 'FLAT'
print("%s FLAT found" % np.sum(ind_flat))
#flat = ccdproc.combine(','.join(t['fps'][ind_flat]), unit='adu', method='median')

ind_flati2 = t['IMAGETYP'] == 'FLATI2'
print("%s FLATI2 found" % np.sum(ind_flati2))
#flat = ccdproc.combine(','.join(t['fps'][ind_flat]), unit='adu', method='median')

ind_thar = t['IMAGETYP'] == 'THAR'
print("%s THAR found" % np.sum(ind_thar))
#thar = ccdproc.combine(','.join(t['fps'][ind_thar]), unit='adu', method='median')

ind_star = t['IMAGETYP'] == 'STAR'
print("%s STAR found" % np.sum(ind_star))
#flat_bias = ccdproc.subtract_bias(flat, bias)

#%%

""" Y shift """

sub_flat = np.where(ind_flat)[0]
sub_flati2 = np.where(ind_flati2)[0]
sub_star = np.where(ind_star)[0]
sub_thar = np.where(ind_thar)[0]
sub_bias = np.where(ind_bias)[0]

if len(sub_flat)>0:
    t['astemplate'][sub_flat[0]] = True
    flat_temp = ccdproc.CCDData.read(t['fps'][sub_flat[0]], unit='adu')
else:
    t['astemplate'][sub_star[0]] = True
    flat_temp = ccdproc.CCDData.read(t['fps'][sub_star[0]], unit='adu')
    
if len(sub_bias)>0:
    t['astemplate'][sub_bias[0]] = True
    bias_temp = ccdproc.CCDData.read(t['fps'][sub_bias[0]], unit='adu')
else:
    bias_temp = ccdproc.CCDData(np.ones((2048, 2048))*300, unit='adu')
flat_temp = ccdproc.subtract_bias(flat_temp, bias_temp)


#%%    

fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(111)

sub = sub_flati2    
print("----- FLATI2 -----")
if len(sub)>0:
    drifts = measure_xshift_2dcorr(t['fps'][sub], bias_temp, flat_temp, xmax=12)
    plt.plot(t['MJD-MID'][sub], drifts, 'o', ms=20, mec='r', mfc='None', label='FLATI2')
    for i, this_drift in zip(sub, drifts): 
        t['xdrift'][i] = this_drift
    
sub = sub_flat
print("------ FLAT ------")
if len(sub)>0:
    drifts = measure_xshift_2dcorr(t['fps'][sub], bias_temp, flat_temp, xmax=12)
    plt.plot(t['MJD-MID'][sub], drifts, 'o', ms=20, mec='b', mfc='None', label='FLAT')
    for i, this_drift in zip(sub, drifts): 
        t['xdrift'][i] = this_drift
        
sub = sub_thar
print("------ THAR ------")
if len(sub)>0:
    drifts = measure_xshift_2dcorr(t['fps'][sub], bias_temp, flat_temp, xmax=12)
    plt.plot(t['MJD-MID'][sub], drifts, '^', ms=20, mec='k', mfc='None', label='THAR')
    for i, this_drift in zip(sub, drifts): 
        t['xdrift'][i] = this_drift
        
sub = sub_star
print("------ STAR ------")
if len(sub)>0:
    drifts = measure_xshift_2dcorr(t['fps'][sub], bias_temp, flat_temp, xmax=12)
    plt.plot(t['MJD-MID'][sub], drifts, 's-', c='c', ms=20, mec='c', mfc='None', label='STAR')
    for i, this_drift in zip(sub, drifts): 
        t['xdrift'][i] = this_drift
        
plt.grid()
l = plt.legend()
l.set_frame_on(False)
#fig.set_figheight(6)
#fig.set_figwidth(12)
plt.xlabel('MJD-MID (date:%s)'%day)
plt.ylabel("DRIFT/pixel")
fig.tight_layout()

ylim = ax.get_ylim()
plt.ylim(ylim[0]-2, ylim[1]+2)

#%%
figpath_pdf = "/hydrogen/song/figs/Xdrift_%s.pdf" % day
figpath_png = "/hydrogen/song/figs/Xdrift_%s.png" % day

fig.savefig(figpath_pdf)
print(figpath_pdf)
fig.savefig(figpath_png)
print(figpath_png)

#%%
figpath_fits = "/hydrogen/song/figs/t_%s.fits" % day

for i, colname in enumerate(t.colnames):
    if t[colname].dtype==np.dtype('O'):
        newcol = t[colname].astype('str')
        t.remove_column(colname)
        t.add_column(newcol, i)

t.write(figpath_fits, format="fits", overwrite=True)
