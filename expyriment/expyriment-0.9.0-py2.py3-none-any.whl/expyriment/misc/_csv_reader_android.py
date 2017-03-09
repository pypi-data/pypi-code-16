"""An emulation of the csv.reader module.

"""
from __future__ import absolute_import, print_function, division
from builtins import *

__author__ = 'Florian Krause <florian@expyriment.org>, \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.9.0'
__revision__ = 'c4963ac'
__date__ = 'Thu Mar 9 13:48:59 2017 +0100'


def reader(the_file):
    '''
    This is a 'dirty' emulation of the csv.reader module only used for 
    Expyriment loading designs under Android. The function reads in a csv file
    and returns a 2 dimensional array.
    
    Parameters
    ----------
    the_file: iterable
        The file to be parsed.
    
    Notes
    -----
    It is strongly suggested the use, if possible, the csv package from the 
    Python standard library.
   
    
    '''
    delimiter = ","
    rtn = []
    for row in the_file:
        rtn.append([strn.strip() for strn in row.split(delimiter)])
    return rtn

