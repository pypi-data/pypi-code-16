#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Thu Feb 09 14:39:42 CET 2017

import os
import numpy
import pkg_resources


from bob.bio.pericrosseye_competition.competition import ISV, GrassmanGaborJet
from bob.bio.pericrosseye_competition.preprocessor import RawCrop
from bob.bio.face.extractor import DCTBlocks, GridGraph
import bob.io.base
import bob.io.base.test_utils
import os
from subprocess import call

def test_isv_system():
    #
    #Test ISV System
    #

    # Image for enrollment
    filename = pkg_resources.resource_filename(__name__, 'data/periocular_model.bmp')
    image_enroll = bob.io.base.load(filename)
    
    # Image for probing
    filename = pkg_resources.resource_filename(__name__, 'data/periocular_probe.bmp')
    image_probe = bob.io.base.load(filename)
    
    # Temporary template 
    template_filename = pkg_resources.resource_filename(__name__, 'data/template_temp.hdf5')    
    
    # Preparing the elements for the authentication
    preprocessor = RawCrop(cropped_image_size=(75, 75), color_channel='gray')
    extractor = DCTBlocks(block_size = 12, block_overlap = 11, number_of_dct_coefficients = 45)

    #algorithm = bob.bio.gmm.algorithm.ISV(subspace_dimension_of_u = 50,number_of_gaussians = 512)
    background_model_path = pkg_resources.resource_filename(__name__, 'data/background_model.hdf5')
    authentication_method = ISV(preprocessor, extractor, background_model_path=background_model_path)
    authentication_method.enroll(image_enroll, template_filename)    
    score = authentication_method.scoring(image_probe, template_filename)
    os.remove(template_filename)
    assert score > 0


def test_grassmanjet_system():
    #
    #Test Grassman Jet System
    #

    # Image for enrollment
    filename = pkg_resources.resource_filename(__name__, 'data/periocular_model.bmp')
    image_enroll = bob.io.base.load(filename)
    
    # Image for probing
    filename = pkg_resources.resource_filename(__name__, 'data/periocular_probe.bmp')
    image_probe = bob.io.base.load(filename)
    
    # Temporary template 
    template_filename = pkg_resources.resource_filename(__name__, 'data/template_temp.hdf5')
    
    # Preparing the elements for the authentication
    preprocessor = RawCrop(cropped_image_size=(75, 75), color_channel='gray')
    extractor = GridGraph(node_distance=5)

    #algorithm = bob.bio.gmm.algorithm.ISV(subspace_dimension_of_u = 50,number_of_gaussians = 512)
    background_model_path = pkg_resources.resource_filename(__name__, 'data/background_gfk.hdf5')
    authentication_method = GrassmanGaborJet(preprocessor, extractor, background_model_path=background_model_path)
    authentication_method.enroll(image_enroll, template_filename)    
    score = authentication_method.scoring(image_probe, template_filename)
    os.remove(template_filename)
    assert score > 0



def test_isv_enroll_match_parsing():
    #
    #Testing the ISV parsing for enrollment
    #

    # Enroll
    filename = pkg_resources.resource_filename(__name__, 'data/periocular_model.bmp')
    template_file = "template.hdf5"
    result_file = "result_file.txt"
    command = "./bin/perienroll_idiap.py {0} {1} {2} -v".format(filename, template_file, result_file)
    call(command.split(" "))
    
    assert os.path.exists(result_file)
    assert os.path.exists(template_file)
    assert float(open(result_file).read())==1
    os.remove(result_file)

    # Match
    filename = pkg_resources.resource_filename(__name__, 'data/periocular_probe.bmp')
    command = "./bin/perimatch_idiap.py {0} {1} {2} -v".format(filename, template_file, result_file)
    call(command.split(" "))
    
    assert os.path.exists(result_file)
    assert os.path.exists(template_file)
    assert float(open(result_file).read()) >= 0

    os.remove(template_file)
    os.remove(result_file)


def test_grassmanjet_enroll_match_parsing():
    #
    # Testing the Grassman Gabor parsing for enrollment
    #

    # Enroll
    filename = pkg_resources.resource_filename(__name__, 'data/periocular_model.bmp')
    template_file = "template.hdf5"
    result_file = "result_file.txt"
    command = "./bin/perienroll_idiap_gfk.py {0} {1} {2} -v".format(filename, template_file, result_file)
    call(command.split(" "))
    
    assert os.path.exists(result_file)
    assert os.path.exists(template_file)
    assert float(open(result_file).read())==1
    os.remove(result_file)

    # Match
    filename = pkg_resources.resource_filename(__name__, 'data/periocular_probe.bmp')
    command = "./bin/perimatch_idiap_gfk.py {0} {1} {2} -v".format(filename, template_file, result_file)
    call(command.split(" "))
    
    assert os.path.exists(result_file)
    assert os.path.exists(template_file)
    assert float(open(result_file).read()) >= 0

    os.remove(template_file)
    os.remove(result_file)

