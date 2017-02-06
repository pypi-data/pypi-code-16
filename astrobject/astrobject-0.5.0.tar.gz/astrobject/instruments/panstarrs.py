#! /usr/bin/env python
# -*- coding: utf-8 -*-
#! /usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
import numpy as np

# - astropy
from astropy.io      import fits as pf
from astropy         import time

# - local dependencies
from .baseinstrument    import Instrument
from ..photometry       import get_photopoint
from ..utils.decorators import _autogen_docstring_inheritance
from ..utils.tools      import kwargs_update

PANSTARRS_INFO= {"bands":[],
                 "telescope":{
                     "lon": None,
                     "lat": None}}
"""
Info from Magnier 2016
Seeing:
the median image quality for the 3π survey is FWHM = (1.31, 1.19, 1.11, 1.07, 1.02) 
arcseconds for (gP1,rP1,iP1,zP1,yP1), with a floor of ∼ 0.7 arcseconds

"""
                 
DATAINDEX = 0


# -------------------- #
# - Instrument Info  - #
# -------------------- #
    
def panstarrs(*args,**kwargs):
    return PanSTARRS(*args,**kwargs)

def is_panstarrs_file(filename):
    """This test if the input file is a GALEX one. Test if 'MPSTYPE' is in the header """
    # not great but this is the structure of MJC images
    return "PSCAMERA" in pf.getheader(filename).keys()

def which_band_is_file(filename):
    """This resuts the band of the given file if it is a
    sdss one"""
    if not is_panstarrs_file(filename):
        return None
        
    h_ = pf.getheader(filename)
    return h_.header.get("HIERARCH FPA.FILTER",None).split(".")[0]
    
def which_obs_mjd(filename):
    """ read the galex-filename and return the
    modified julian date """
    if not is_panstarrs_file(filename):
        return None
    h_ = pf.getheader(filename)
    return h_.get("MJD-OBS")



class PanSTARRS( Instrument ):
    """ """
    @property
    def mab0(self):
        return self.header["HIERARCH FPA.ZP"]
    @property
    def bandname(self):
        """ band of the image. """
        return self.header.get("HIERARCH FPA.FILTER",None).split(".")[0]

    @property
    def mjd(self):
        return self.header["MJD-OBS"]
