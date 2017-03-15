#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Wed 11 May 2016 09:39:36 CEST

"""
Do the matching using Intersession Variability Modelling

Usage:
  perimatch_idiap.py <image_file> <template_file> <output_file> [-v]
  perimatch_idiap.py -h | --help
Options:
  -h --help           Show this screen.
  -v                  Verbosity level
"""

import bob.bio.face
import bob.io.image
import bob.io.base
import os
import pkg_resources
import logging

from bob.bio.pericrosseye_competition.competition import ISV
from bob.bio.pericrosseye_competition.preprocessor import RawCrop
from bob.bio.face.extractor import DCTBlocks
from .utils import compute_stats, apply_norm

logger = logging.getLogger("bob.bio.pericrosseye_competition")
import bob.core

# For the time beeing this stats are hard coded
ma = 3.29813019
mi = -0.40391332

def main():
    from docopt import docopt

    args = docopt(__doc__, version='Compute scores using ISV system')

    probe_file = args["<image_file>"]
    template_file = args["<template_file>"]
    output_file = args["<output_file>"]
    verbose = args["-v"]

    if verbose:
        bob.core.log.set_verbosity_level(logger, 3)
    
    image_probe = bob.io.base.load(probe_file)
    logger.info("Loading preprocessors")
    preprocessor = RawCrop(cropped_image_size=(75, 75), color_channel='gray')  
    extractor = DCTBlocks(block_size = 12, block_overlap = 11, number_of_dct_coefficients = 45)
    background_model_path = pkg_resources.resource_filename("bob.bio.pericrosseye_competition.test", 'data/background_model.hdf5')
    
    logger.info("Loading Background model")
    authentication_method = ISV(preprocessor, extractor, background_model_path=background_model_path)
    try:
        logger.info("Computing score ....")
        result = apply_norm(authentication_method.scoring(image_probe, template_file), mi, ma)        
        logger.info("Done ....")
    except:
        result = -1

    #Clipping
    if result < 0:
        result = 0
    if result > 1:
        result = 1

    # Write output
    open(output_file, 'w').write(str(result))

