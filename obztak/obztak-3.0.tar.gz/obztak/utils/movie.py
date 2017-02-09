#!/usr/bin/env python
"""
Generic python script.
"""
__author__ = "Alex Drlica-Wagner"

import os
from os.path import expandvars
import shutil
import time
import logging
import tempfile
import subprocess
import warnings
from collections import OrderedDict as odict

import matplotlib
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
import pylab as plt
import numpy as np
import ephem

from obztak.utils.ortho import makePlot,plotField, setdefaults, COLORS
from obztak.utils import constants
from obztak.utils import fileio
from obztak.field import FieldArray
from obztak.utils.date import datestring,nite2utc,utc2nite,get_nite
from obztak.ctio import CTIO

def draw_field(field, target_fields=None, completed_fields=None, **kwargs):
    """
    Plot a specific target field.
    """
    defaults = dict(edgecolor='none', s=50, vmin=0, vmax=4, cmap='summer_r')
    #defaults = dict(edgecolor='none', s=50, vmin=0, vmax=4, cmap='gray_r')
    setdefaults(kwargs,defaults)

    if isinstance(field,np.core.records.record):
        tmp = FieldArray(1)
        tmp[0] = field
        field = tmp

    msg = "%s (date=%s, "%(field['ID'][0],datestring(field['DATE'][0],0))
    msg +="ra=%(RA)-6.2f, dec=%(DEC)-6.2f, secz=%(AIRMASS)-4.2f)"%field[0]
    print(msg)
    #logging.info(msg)

    defaults = dict(date=field['DATE'][0], name='ortho')
    options_basemap = dict()
    setdefaults(options_basemap,defaults)
    fig, basemap = makePlot(**options_basemap)

    # Plot target fields
    if target_fields is not None:
        proj = basemap.proj(target_fields['RA'], target_fields['DEC'])
        basemap.scatter(*proj, c=np.zeros(len(target_fields))+0.3, **kwargs)

    # Plot completed fields
    if completed_fields is not None:
        proj = basemap.proj(completed_fields['RA'],completed_fields['DEC'])
        basemap.scatter(*proj, c=completed_fields['TILING'], **kwargs)

    # Try to draw the colorbar
    try:
        if len(fig.axes) == 2:
            # Draw colorbar in existing axis
            colorbar = plt.colorbar(cax=fig.axes[-1])
        else:
            colorbar = plt.colorbar()
        colorbar.set_label('Tiling')
    except TypeError:
        pass

    # Show the selected field
    proj = basemap.proj(field['RA'], field['DEC'])
    basemap.scatter(*proj, c=COLORS[field[0]['FILTER']],edgecolor='none',s=50)

def animate_ortho(fields=None,target_fields=None,completed_fields=None):
    if fields is None:
        fields = completed_fields[-1]

    if isinstance(fields,np.core.records.record):
        tmp = FieldArray(1)
        tmp[0] = fields
        fields = tmp
    kwargs = dict()
    if completed_fields is None: completed_fields = FieldArray()
    ims = []
    for i,f in enumerate(fields):
        draw_field(fields[i],target_fields,completed_fields,**kwargs)
        plt.savefig('tmp_%s.png'%i)
        completed_fields = completed_fields + fields[[i]]

    im_ani = animation.ArtistAnimation(plt.gcf(), ims)
    #im_ani.save('im.mp4')

    return ims,im_ani

def animate(i):
    plot


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()
