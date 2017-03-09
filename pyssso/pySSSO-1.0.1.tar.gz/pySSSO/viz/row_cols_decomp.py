#!/usr/bin/env python

#-------------
# Load modules
#-------------
import sys
import math


#-----------------------------------

def calc_rows_columns(n, nColumns=None):
    """
      Takes a number n and decomposes it into nrows and ncols
      so that n = nrows*ncols.

      Required input:
        - n: a positive integer

      Returned value:
        - nrows,ncols: integers given by n = nrows*ncols
    """

    if (nColumns == None):
       a = math.sqrt(n)
       nrows = int(math.ceil(a))

       done = False

       while not(done):
          if ((n % nrows) == 0):
             ncols = int(n / nrows)
             done = True
          else:
             nrows = nrows + 1
    else:
        nrows = int(n / nColumns)
        if (nrows*nColumns < n):
           nrows = nrows + 1
        ncols = nColumns

    return nrows, ncols
