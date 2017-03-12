import os
import time

import logging

import speech_recognition as sr
from flask import Flask

from kalliope import Utils
from kalliope.core.ConfigurationManager import SettingLoader
from kalliope.core.ResourcesManager import ResourcesManager

from kalliope.core.ConfigurationManager import BrainLoader

from kalliope.core.RestAPI.FlaskAPI import FlaskAPI
from kalliope.stt.bing import Bing
from kalliope.stt.cmusphinx import Cmusphinx
from kalliope.stt.google import Google

logging.basicConfig()
logger = logging.getLogger("kalliope")
logger.setLevel(logging.INFO)



def _get_global_variable(sentence, settings):
    """
    Get the global variable from the sentence with brackets
    :param sentence: the sentence to check
    :return: the global variable
    """
    sentence_no_spaces = Utils.remove_spaces_in_brackets(sentence=sentence)
    list_of_bracket_params = Utils.find_all_matching_brackets(sentence=sentence_no_spaces)
    for param_with_bracket in list_of_bracket_params:
        param_no_brackets = param_with_bracket.replace("{{", "").replace("}}", "")
        if param_no_brackets in settings.variables:
            logger.debug("Replacing variable %s with  %s" % (param_with_bracket,
                                                             settings.variables[param_no_brackets]))
            sentence_no_spaces = sentence_no_spaces.replace(param_with_bracket,
                                                            str(settings.variables[param_no_brackets]))
    return sentence_no_spaces


def replace_global_variables(parameter):

    if isinstance(parameter, dict):
        print "parameter is dict %s" % str(parameter)
        for key, value in parameter.iteritems():
            parameter[key] = replace_global_variables(value)
        return parameter
    if isinstance(parameter, list):
        print "parameter is list %s" % str(parameter)
        new_parameter_list = list()
        for el in parameter:
            new_parameter_list.append(replace_global_variables(el))
        return new_parameter_list
    if isinstance(parameter, str):
        print "parameter is string %s" % str(parameter)
        if Utils.is_containing_bracket(parameter):
            return _get_global_variable(parameter, sl.settings)
        return parameter


sl = SettingLoader()
settings = sl.settings

param1 = {'message': 'salut {{ name }}'}
param2 = {'from_answer_link': [{'synapse': 'synapse2', 'answers': ['absolument', '{{ name }}']}, {'synapse': 'synapse3', 'answers': ['{{ name }}']}], 'default': 'synapse4'}


# param1_updated = replace_global_variables(param1)
# print param1_updated

param2_updated = replace_global_variables(param2)
print param2_updated

