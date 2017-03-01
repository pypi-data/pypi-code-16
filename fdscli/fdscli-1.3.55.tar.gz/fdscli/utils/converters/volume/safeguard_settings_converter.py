# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
'''
Created on Dec 28, 2016

@author: nate
'''
from fdscli.model.volume.safeguard_settings import SafeGuardSettings
import json

class SafeGuardSettingsConverter(object):
    '''
    Created on Dec 27, 2016

    @author: nate
    '''
    @staticmethod
    def build_settings_from_json( jsonData ):

        if not isinstance(jsonData, dict):
            jsonData = json.loads(jsonData);

        settings = SafeGuardSettings()
        
        settings.safeguard_type = jsonData.pop( "type", None )
        
        return settings
        
    @staticmethod
    def to_json( settings ):        
        
        d = dict()
        
        if settings is None:
            settings = SafeGuardSettings()
        
        d["type"] = settings.safeguard_type
        
        result = json.dumps( d )
        
        return result
