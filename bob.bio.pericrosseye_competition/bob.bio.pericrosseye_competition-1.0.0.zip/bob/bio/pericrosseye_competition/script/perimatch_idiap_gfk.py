#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Wed 11 May 2016 09:39:36 CEST

"""
Do the matching using the Gabor Graph with Geodesic Flow Kernel

Usage:
  perimatch_idiap_gfk.py <template_file_A> <template_file_B> <output_file> [-v]
  perimatch_idiap_gfk.py -h | --help
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

from bob.bio.pericrosseye_competition.competition import GrassmanGaborJet
from bob.bio.pericrosseye_competition.preprocessor import RawCrop
from bob.bio.pericrosseye_competition.extractor import EyeGraph
from .utils import apply_norm

logger = logging.getLogger("bob.bio.pericrosseye_competition")
import bob.core

# For the time beeing this stats are hard coded
ma = 6.3462370100000003
mi = -0.60996388999999995


def main():
    from docopt import docopt

    args = docopt(__doc__, version='Scoring a client using GaborJets in the grassman manifolds')

    image_file = args["<template_file_A>"]
    template_file = args["<template_file_B>"]
    output_file = args["<output_file>"]
    verbose = args["-v"]

    if verbose:
        bob.core.log.set_verbosity_level(logger, 3)
    
    #image_probe = bob.io.base.load(image_file)
    logger.info("Loading preprocessors")
    preprocessor=RawCrop(cropped_image_size=(800 , 900), color_channel='gray')
    
    extractor = EyeGraph(distances = [50, 100, 150, 200, 250],
                         n_points  = 20,
                         landmark_offset=20)
    
    background_model_path = pkg_resources.resource_filename("bob.bio.pericrosseye_competition.test", 'data/background_gfk.hdf5')
    
    logger.info("Loading Background model")
    authentication_method = GrassmanGaborJet(preprocessor, extractor, 
     background_model_path=background_model_path)

    try:
        logger.info("Scoring ....")
        # Now we will deal with the template not with the image itself
        result = apply_norm(authentication_method.scoring(image_file, template_file), mi, ma)
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

