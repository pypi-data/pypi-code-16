# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
A Python package for the quantitative analysis of the interaction of energetic photons with matter (x-rays and gamma-rays).
"""
import os
import json
# Affiliated packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from ._astropy_init import *
# ----------------------------------------------------------------------------

# For egg_info test builds to pass, put package imports here.
if not _ASTROPY_SETUP_:
    _package_directory = os.path.dirname(os.path.abspath(__file__))
    _data_directory = os.path.abspath(os.path.join(_package_directory, 'data'))

    with open(os.path.join(_data_directory, 'elements.json')) as data_file:
        elements_list = json.load(data_file)

    with open(os.path.join(_data_directory, 'compounds_mixtures.json')) as data_file:
        compounds_mixtures_list = json.load(data_file)

    material_list = elements_list.copy()
    material_list.update(compounds_mixtures_list)
