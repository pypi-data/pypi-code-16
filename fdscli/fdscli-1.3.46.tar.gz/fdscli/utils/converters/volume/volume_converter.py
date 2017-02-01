# Copyright 2015 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.volume.volume import Volume
from fdscli.utils.converters.volume.qos_policy_converter import QosPolicyConverter
from fdscli.utils.converters.volume.settings_converter import SettingsConverter
from fdscli.utils.converters.volume.volume_status_converter import VolumeStatusConverter
from fdscli.utils.converters.volume.data_protection_policy_converter import DataProtectionPolicyConverter
from fdscli.utils.converters.volume.safeguard_settings_converter import SafeGuardSettingsConverter
from fdscli.utils.converters.admin.tenant_converter import TenantConverter

class VolumeConverter( object ):
    '''
    Created on Apr 14, 2015
    
    Because we plan on using generated object models we needed a separate mechanism for marshalling
    volume objects between the python class representation and the JSON dictionary objects.  
    
    This is that mechanism
    
    @author: nate
    '''
        
    @staticmethod
    def build_volume_from_json( j_str ):
        '''Produce a ``model.Volume`` object from deserialized server response.

        Parameters
        ----------
        :type j_str: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type ``model.task.SafeGuardTaskStatus``
        '''
        volume = Volume();
        
        if not isinstance( j_str, dict ):
            j_str = json.loads(j_str)

        volume.id = j_str.pop( "uid", volume.id )
        volume.name = j_str.pop( "name", volume.name )
        
        ctime = j_str.pop( "created", volume.creation_time )
    
        volume.creation_time = ctime["seconds"]
         
        volume.status = VolumeStatusConverter.build_status_from_json(j_str.pop("status"))
        volume.media_policy = j_str.pop("mediaPolicy", volume.media_policy)
        volume.application = j_str.pop("application", volume.application)
        volume.qos_policy = QosPolicyConverter.build_policy_from_json(j_str.pop("qosPolicy"))
        volume.data_protection_policy = DataProtectionPolicyConverter.build_policy_from_json(j_str.pop("dataProtectionPolicy"))
        
        if "tenant" in j_str:
            volume.tenant = TenantConverter.build_tenant_from_json(j_str.pop( "tenant", volume.tenant ))
            
        tempSettings = j_str.pop( "settings", volume.settings )
        
        volume.settings = SettingsConverter.build_settings_from_json( tempSettings )
        
        if "safeGuardDescriptor" in j_str:
            volume.safeguard_settings = SafeGuardSettingsConverter.build_settings_from_json( j_str.pop("safeGuardDescriptor") )
        
        return volume
    
    @staticmethod
    def to_json( volume ):
        '''
        This will take a volume object and turn it into a JSON dictionary object compatible with the
        json module
        '''
        
        d = dict()
        
        d["uid"] = volume.id
        d["name"] = volume.name
        
        j_qos = QosPolicyConverter.to_json(volume.qos_policy)
        
        d["qosPolicy"] = json.loads(j_qos)
        d["mediaPolicy"] = volume.media_policy

        j_settings = SettingsConverter.to_json(volume.settings)
        d["settings"] = json.loads(j_settings)

        j_status = VolumeStatusConverter.to_json(volume.status)
        d["status"] = json.loads(j_status)
        
        j_d_policy = DataProtectionPolicyConverter.to_json(volume.data_protection_policy)
        d["dataProtectionPolicy"] = json.loads(j_d_policy)
        
        d["application"] = volume.application
        
        if volume.tenant is not None:
            d["tenant"] = json.loads(TenantConverter.to_json(volume.tenant));
        
        ctime = dict()
        ctime["seconds"] = volume.creation_time
        ctime["nanos"] = 0
        
        d["created"] = ctime
        
        j_safeguard = SafeGuardSettingsConverter.to_json(volume.safeguard_settings)
        d["safeGuardDescriptor"] = json.loads(j_safeguard)

        result = json.dumps( d )
        
        return result
