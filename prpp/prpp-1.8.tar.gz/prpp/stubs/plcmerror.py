#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
from .plcm import Plcm

class PlcmError(Plcm):

    root_element = "plcm-error"
    target_namespace = "urn:com:polycom:api:rest:plcm-error"
    imported_namespaces = None
    element_properties={
        'status-code':{'tag':'status-code','prop':'status_code'},
        'description':{ 'tag':'description','prop':'description'},
        'technical-details':{ 'tag':'technical-details','prop':'technical_details'},
        'detailed-error-code':{ 'tag':'detailed-error-code','prop':'detailed_error_code'},
        'localization-key':{ 'tag':'localization-key','prop':'localization_key'},
        'localization-param':{ 'tag':'localization-param','prop':'localization_param'},
    }

    def __init__(self, name=None):
        self.name = name
    
    def __str__(self):
        return '[ERR] %s %s' % (self.status_code, self.description)