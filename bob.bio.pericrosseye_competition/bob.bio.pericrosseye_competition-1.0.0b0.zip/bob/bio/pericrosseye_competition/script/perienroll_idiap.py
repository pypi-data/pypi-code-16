#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Wed 11 May 2016 09:39:36 CEST

"""
Enroll a client using Intersession Variability Modelling

Usage:
  perienroll_idiap.py <image_file> <template_file> <output_file> [-v]
  perienroll_idiap.py -h | --help
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

logger = logging.getLogger("bob.bio.pericrosseye_competition")
import bob.core


def main():
    from docopt import docopt

    args = docopt(__doc__, version='Enroll a client using ISV')

    image_file = args["<image_file>"]
    template_file = args["<template_file>"]
    output_file = args["<output_file>"]
    verbose = args["-v"]

    if verbose:
        bob.core.log.set_verbosity_level(logger, 3)
    
    image_enroll = bob.io.base.load(image_file)
    logger.info("Loading preprocessors")
    preprocessor = RawCrop(cropped_image_size=(75, 75), color_channel='gray')  
    extractor = DCTBlocks(block_size = 12, block_overlap = 11, number_of_dct_coefficients = 45)
    background_model_path = pkg_resources.resource_filename("bob.bio.pericrosseye_competition.test", 'data/background_model.hdf5')
    
    logger.info("Loading Background model")
    authentication_method = ISV(preprocessor, extractor, 
     background_model_path=background_model_path)

    try:
        logger.info("Enrolling ....")
        authentication_method.enroll(image_enroll, template_file)
        logger.info("Done ....")      
        result = 1
    except:
        result = 0
        
    # Write output
    open(output_file, 'w').write(str(result))

