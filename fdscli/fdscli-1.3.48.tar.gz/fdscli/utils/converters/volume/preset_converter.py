# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

from fdscli.model.volume.data_protection_policy_preset import DataProtectionPolicyPreset
from fdscli.model.volume.qos_preset import QosPreset
from fdscli.model.volume.recurrence_rule import RecurrenceRule
from fdscli.model.volume.safeguard_preset import SafeGuardPreset
from fdscli.utils.converters.volume.recurrence_rule_converter import RecurrenceRuleConverter
from fdscli.utils.converters.volume.snapshot_policy_converter import SnapshotPolicyConverter
import json

class PresetConverter(object):
    '''
    Created on May 6, 2015
    
    @author: nate
    '''

    @staticmethod
    def build_qos_preset_from_json( j_qos_preset ):
        '''Produce a QoS preset given a JSON document.

        Parameters
        ----------
        :type j_qos_preset: string or dict
        :param j_qos_preset: JSON document for a QoS preset

        Returns
        -------
        :type ``model.volume.QosPreset`` object
        '''
        # Produces Python object representation if given argument is a string instance
        if not isinstance(j_qos_preset, dict):
            j_qos_preset = json.loads(qos_preset)

        qos = QosPreset()
        qos.id = j_qos_preset.pop("id", qos.id)
        qos.name = j_qos_preset.pop("name", "UNKNOWN")
        qos.iops_guarantee = j_qos_preset.pop("iopsMin", qos.iops_min)
        qos.iops_limit = j_qos_preset.pop("iopsMax", qos.iops_max)
        qos.priority = j_qos_preset.pop("priority", qos.priority)
        
        return qos
    
    @staticmethod
    def build_safeguard_preset_from_json( j_safeguard_preset ):
        '''Produce a SafeGuard preset given a JSON document.

        Parameters
        ----------
        :type j_safeguard_preset: string or dict
        :param j_safeguard_preset: JSON document for a SafeGuard preset

        Returns
        -------
        :type ``model.volume.SafeGuardPreset`` object
        '''
        # Produces Python object representation if given argument is a string instance
        if not isinstance(j_safeguard_preset, dict):
            j_safeguard_preset = json.loads(j_safeguard_preset)

        preset = SafeGuardPreset()
        preset.id = j_safeguard_preset.pop("uid", preset.id)
        preset.name = j_safeguard_preset.pop("name", "UNKNOWN")
        r = j_safeguard_preset.pop("recurrenceRule", preset.recurrence_rule)
        if not isinstance(r, RecurrenceRule):
            preset.recurrence_rule = RecurrenceRuleConverter.build_rule_from_json(r)

        return preset

    @staticmethod
    def build_timeline_from_json( j_timeline_preset ):
        '''Produce a data protection policy preset given a JSON document.

        Parameters
        ----------
        :type j_timeline_preset: string or dict
        :param j_timeline_preset: JSON document for a data protection policy preset

        Returns
        -------
        :type ``model.volume.DataProtectionPolicyPreset`` object
        '''
        # Produces Python object representation if given argument is a string instance
        if not isinstance(j_timeline_preset, dict):
            j_timeline_preset = json.loads(j_timeline_preset)

        timeline = DataProtectionPolicyPreset()
        timeline.id = j_timeline_preset.pop("id", timeline.id)
        timeline.name = j_timeline_preset.pop("name", "UNKNOWN")

        cD = j_timeline_preset.pop( "commitLogRetention" )
        timeline.continuous_protection = cD["seconds"]

        #If I don't do this, the list is still populated with previous list... no idea why
        timeline.policies = list()

        policies = j_timeline_preset.pop("snapshotPolicies", [])

        for policy in policies:
            timeline.policies.append( SnapshotPolicyConverter.build_snapshot_policy_from_json( policy ))

        return timeline

    @staticmethod
    def qos_to_json( preset ):
        '''
        Turn a qos preset into JSON
        '''
        d = dict()
        
        d["id"] = preset.id
        d["name"] = preset.name
        d["priority"] = preset.priority
        d["iopsMin"] = preset.iops_min
        d["iopsMax"] = preset.iops_max
        
        j_str = json.dumps( d )
        
        return j_str

    @staticmethod
    def safeguard_to_json_string(preset):
        '''
        Parameters
        ----------
        :type preset: ``model.volume.SafeGuardPreset``

        Returns
        -------
        :type string instance containing a JSON document
        '''
        if not isinstance(preset, SafeGuardPreset):
            raise TypeError()

        d = dict()

        d["uid"] = preset.id
        d["name"] = preset.name
        j_obj = json.loads(RecurrenceRuleConverter.to_json(preset.recurrence_rule))
        # The type of j_obj is <type 'dict'>
        d["recurrenceRule"] = j_obj

        # Serialize dictionary object to a JSON formatted string
        j_str = json.dumps(d)
        return j_str

    @staticmethod
    def timeline_to_json(preset):
        '''
        Turn a timeline policy preset into a JSON string
        '''
