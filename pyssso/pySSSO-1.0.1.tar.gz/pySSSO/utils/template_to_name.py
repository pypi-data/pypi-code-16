#!/usr/bin/env python

import sys

def tmpl_2_name(tmpl, **keywords):
    """
      Takes a file template and derives a file name using the keywords:
    
          YYYY = ...   year
            MM = ...   month
            DD = ...   day
            HH = ...   hour
            NN = ...   minute
            SS = ...   second
    
      If the file template is:
         tmpl = /discover/nobackup/outputs/%y4/emiss/sample.%y4%m2%d2_00z.nc
      the call of 
         tmpl_2_name(tmpl, YYYY=2004, MM=02, DD=21)
      will produce:
         fName = /discover/nobackup/outputs/2004/emiss/sample.20040221_00z.nc
    """
    fname = tmpl
    for kw in keywords.keys():
        word = str(keywords[kw])
        if len(word) == 1:
           word = '0'+word
        if (kw == 'YYYY'): fname = fname.replace( '%y4', word )
        if (kw == 'MM'):   fname = fname.replace( '%m2', word )
        if (kw == 'DD'):   fname = fname.replace( '%d2', word )
        if (kw == 'HH'):   fname = fname.replace( '%h2', word )
        if (kw == 'NN'):   fname = fname.replace( '%n2', word )
        if (kw == 'SS'):   fname = fname.replace( '%s2', word )
    return fname
