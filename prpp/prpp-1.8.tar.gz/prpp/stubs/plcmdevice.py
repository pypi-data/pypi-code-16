#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
from .plcm import Plcm

GATEKEEPER_STATUS_ENUM={
    'UNKNOWN':'UNKNOWN',
    'REGISTERED':'REGISTERED',
    'NOT_REGISTERED':'NOT_REGISTERED',
    'REGISTERING':'REGISTERING',
    'REJECTED':'REJECTED',
    'NOT_APPLICABLE':'NOT_APPLICABLE',
}

GAB_STATUS_ENUM={
    'UNKNOWN':'UNKNOWN',
    'REGISTERED':'REGISTERED',
    'NOT_REGISTERED':'NOT_REGISTERED',
    'NOT_APPLICABLE':'NOT_APPLICABLE',
}

LDAP_STATUS_ENUM={
    'UNKNOWN':'UNKNOWN',
    'REGISTERED':'REGISTERED',
    'NOT_REGISTERED':'NOT_REGISTERED',
    'NOT_APPLICABLE':'NOT_APPLICABLE',
    'BIND_FAILED':'BIND_FAILED',
    'CONNECT_FAILED':'CONNECT_FAILED',
    'INIT_FAILED':'INIT_FAILED',
    'OPTIONSET_FAILED':'OPTIONSET_FAILED',
    'SEARCH_FAILED':'SEARCH_FAILED',
    'SSL_ENABLE_FAILED':'SSL_ENABLE_FAILED',
    'UNSPECIFIED_ERROR':'UNSPECIFIED_ERROR',
}

XMPP_STATUS_ENUM={
    'UNKNOWN':'UNKNOWN',
    'REGISTERED':'REGISTERED',
    'NOT_REGISTERED':'NOT_REGISTERED',
    'NOT_APPLICABLE':'NOT_APPLICABLE',
}

SIP_STATUS_ENUM={
    'UNKNOWN':'UNKNOWN',
    'REGISTERED':'REGISTERED',
    'NOT_REGISTERED':'NOT_REGISTERED',
    'NOT_APPLICABLE':'NOT_APPLICABLE',
}

EXCHANGE_STATUS_ENUM={
    'UNKNOWN':'UNKNOWN',
    'REGISTERED':'REGISTERED',
    'NOT_REGISTERED':'NOT_REGISTERED',
    'NOT_APPLICABLE':'NOT_APPLICABLE',
}

MANAGED_STATUS_ENUM={
    'OK':'OK',
    'UNKNOWN':'UNKNOWN',
    'NOT_APPLICABLE':'NOT_APPLICABLE',
    'NOT_RESPONDING':'NOT_RESPONDING',
    'HEARTBEAT_TIMEOUT':'HEARTBEAT_TIMEOUT',
    'SIGNED_OUT':'SIGNED_OUT',
    'CREDENTIALS_REQUIRED':'CREDENTIALS_REQUIRED',
    'CREDENTIALS_FAILED':'CREDENTIALS_FAILED',
    'HTTP_FORBIDDEN':'HTTP_FORBIDDEN',
    'BEHIND_FIREWALL':'BEHIND_FIREWALL',
    'REBOOTING':'REBOOTING',
    'SSH_SERVER_ERROR':'SSH_SERVER_ERROR',
}

ISDN_LINE_STATUS_ENUM={
    'UNKNOWN':'UNKNOWN',
    'ISDN_LINE_UP':'ISDN_LINE_UP',
    'ISDN_LINE_DOWN':'ISDN_LINE_DOWN',
}

ISDN_ASSIGNEMENT_TYPE_ENUM={
    'UNKNOWN':'UNKNOWN',
    'PREDEFINED':'PREDEFINED',
    'DYNAMIC':'DYNAMIC',
    'AUTOASSIGNED':'AUTOASSIGNED',
    'DEFAULTGW':'DEFAULTGW',
}

DEVICE_STATUS_ENUM={
    'OFFLINE':'OFFLINE',
    'ONLINE':'ONLINE',
    'INCALL':'INCALL',
}


class PlcmDeviceStatus(Plcm):
    
    root_element = 'plcm-device-status'
    target_namespace = "urn:com:polycom:api:rest:plcm-device-status"
    imported_namespaces = []
    
    element_properties={
        'gatekeeper-status-enum':{'tag':'gatekeeper-status-enum','prop':'gatekeeper_status','type':'enum','values':GATEKEEPER_STATUS_ENUM},
        'gab-status-enum':{'tag':'gab-status-enum','prop':'gab_status','type':'enum','values':GAB_STATUS_ENUM},
        'ldap-status-enum':{'tag':'ldap-status-enum','prop':'ldap_status','type':'enum','values':LDAP_STATUS_ENUM},
        'xmpp-status-enum':{'tag':'xmpp-status-enum','prop':'xmpp_status','type':'enum','values':XMPP_STATUS_ENUM},
        'sip-status-enum':{'tag':'sip-status-enum','prop':'sip_status','type':'enum','values':SIP_STATUS_ENUM},
        'exchange-status-enum':{'tag':'exchange-status-enum','prop':'exchange_status','type':'enum','values':EXCHANGE_STATUS_ENUM},
        'managed-status-enum':{'tag':'managed-status-enum','prop':'managed_status','type':'enum','values':MANAGED_STATUS_ENUM},
        'gk-configured-server':{'tag':'gk-configured-server','prop':'gk_configured_server'},
        'sip-configured-server':{'tag':'sip-configured-server','prop':'sip_configured_server'},
        'isdn-line-status-enum':{'tag':'isdn-line-status-enum', 'prop':'isdn_line_status', 'type':'enum', 'values':ISDN_LINE_STATUS_ENUM},
        'isdn-assignment-type-enum':{'tag':'isdn-assignment-type-enum','prop':'isdn_assignment_type','type':'enum', 'values':ISDN_ASSIGNEMENT_TYPE_ENUM},
        'endpoint-isdn-type':{'tag':'endpoint-isdn-type','prop':'endpoint_isdn_type'},
        'device-status-enum':{'tag':'device-status-enum','prop':'device_status','type':'enum', 'values':DEVICE_STATUS_ENUM},
        'device-local-time':{'tag':'device-local-time','prop':'device_local_time'},
    }
    
    def __str__(self, *args, **kwargs):
        return "[DeviceStatus]%s/%s/%s" % (self.device_status, self.gk_configured_server, self.sip_configured_server)
    

MCU_TYPE_ENUM={
    'RMX':'RMX',
    'CODIAN':'CODIAN',
    'MGC':'MGC',
    'OTHER':'OTHER',
}    
SIGNALING_TYPE_ENUM={
    'SIP':'SIP',
    'H323':'H323',
    'SIP_H323':'SIP_H323',
    'XMPP':'XMPP',
    'XMPP_SIP':'XMPP_SIP',
    'UNKNOWN':'UNKNOWN',
}    
        

class PlcmMcuIdentity(Plcm):
    root_element = 'plcm-mcu-identity'
    target_namespace = 'urn:com:polycom:api:rest:plcm-mcu-identity'
    imported_namespaces = ['urn:com:polycom:api:rest:plcm-gateway-profile']
    
    element_properties={
        'mcu-name':{'tag':'mcu-name','prop':'mcu_name'},
        'mcu-type':{'tag':'mcu-type','prop':'mcu_type','type':'enum','values':MCU_TYPE_ENUM},
        'mcu-description':{'tag':'mcu-description','prop':'mcu_description'},
        'management-address':{'tag':'management-address','prop':'management_address'},
        'signaling-types':{'tag':'signaling-types','prop':'signaling_types','type':'enum','values':SIGNALING_TYPE_ENUM},
        'is-gateway':{'tag':'is-gateway','prop':'is_gateway','type':'boolean'},
        'media-address':{'tag':'media-address','prop':'media_address'},
        'vmr-enabled':{'tag':'vmr-enabled','prop':'vmr_enabled','type':'boolean'},
        'dial-string-prefix':{'tag':'dial-string-prefix','prop':'dial_string_prefix'},
        'gateway':{'tag':'gateway', 'prop':'gateway', 'type':''},
        'registered-prefixes':{'tag':'registered-prefixes','prop':'registered_prefixes'},
        'mcu-enabled':{'tag':'mcu-enabled','prop':'mcu_enabled','type':'boolean'},
        'mcu-busyout':{'tag':'mcu-busyout','prop':'mcu_busyout','type':'boolean'},
        'reserved-audio-ports':{'tag':'reserved-audio-ports','prop':'reserved_audio_ports'},
        'reserved-video-ports':{'tag':'reserved-video-ports','prop':'reserved_video_ports'},
    }
    
    def __str__(self, *args, **kwargs):
        return "[McuIdentity]%s/%s/%s" % (self.mcu_name, self.mcu_type, self.management_address)

H323_ALIAS_TYPE_ENUM={
    'H323_ID':'H323_ID',
    'H323_DIALDIGITS':'H323_DIALDIGITS',
    'H323_EMAILID':'H323_EMAILID',
    'H323_MOBILEUIM':'H323_MOBILEUIM',
    'H323_PARTYNUMBER':'H323_PARTYNUMBER',
    'H323_URLID':'H323_URLID',
    'H323_TRANSPORT_ADDRESS':'H323_TRANSPORT_ADDRESS',
    'UNKNOWN':'UNKNOWN',
}

class PlcmH323AliasType(Plcm):
    root_element = 'plcm-h323-alias-type'
    target_namespace = 'urn:com:polycom:api:rest:plcm-h323-alias-type'
    imported_namespaces = None
    
    element_properties={
        'PlcmH323AliasType':{'tag':'PlcmH323AliasType','prop':'name','type':'enum','values':H323_ALIAS_TYPE_ENUM}
    }
    
    def __str__(self, *args, **kwargs):
        return "[H323AliasType]%s" % self.name

class PlcmH323Alias(Plcm):
    root_element = 'plcm-h323-alias'
    target_namespace = 'urn:com:polycom:api:rest:plcm-h323-alias'
    imported_namespaces = ['urn:com:polycom:api:rest:plcm-h323-alias-type','urn:com:polycom:api:rest:plcm-h323-identity']
    
    element_properties={
        'value':{'tag':'value','prop':'value'},
        'plcm-h323-alias-type':{'tag':'plcm-h323-alias-type','prop':'alias_type','type':'enum','values':H323_ALIAS_TYPE_ENUM},
        'mutable':{'tag':'mutable','prop':'is_mutable','type':'boolean'},
    }
    
    def __str__(self, *args, **kwargs):
        return "[H323Alias]%s/%s" % (self.value, self.alias_type)

H323_REGISTRATION_STATE_ENUM={
    'NOT_REGISTERED':'NOT_REGISTERED',
    'INACTIVE':'INACTIVE',
    'ACTIVE':'ACTIVE',
    'BLOCKED':'BLOCKED',
    'QUARANTINED':'QUARANTINED',
    'QUARANTINED_INACTIVE':'QUARANTINED_INACTIVE',
}
H323_TERMINAL_TYPE_ENUM={
    'TERMINAL':'TERMINAL',
    'GATEWAY':'GATEWAY',
    'MCU':'MCU',
    'GATEKEEPER':'GATEKEEPER',
    'UNKNOWN':'UNKNOWN',
}

class PlcmH323Identity(Plcm):
    root_element = 'plcm-h323-identity'
    target_namespace = 'urn:com:polycom:api:rest:plcm-h323-identity'
    imported_namespaces = ['urn:com:polycom:api:rest:plcm-h323-alias',
                           'urn:com:polycom:api:rest:plcm-h323-alias-type']
    
    element_properties={
        'h323-alias':{'tag':'h323-alias','prop':'h323_alias','type':'urn:com:polycom:api:rest:plcm-h323-alias','class':PlcmH323Alias},
        'call-signalling-address':{'tag':'call-signalling-address','prop':'call_signalling_address'},
        'ras-address':{'tag':'ras-address','prop':'ras_address'},
        'registration-active':{'tag':'registration-active','prop':'registration_active','type':'boolean'},
        'h323-registration-state':{'tag':'h323-registration-state','prop':'h323_registration_state','type':'enum','values':H323_REGISTRATION_STATE_ENUM},
        'registration-ttl':{'tag':'registration-ttl','prop':'registration_ttl'},
        'alternate-gk-supported':{'tag':'alternate-gk-supported','prop':'is_alternate_gk_supported','type':'boolean'},
        'terminal-type-data':{'tag':'terminal-type-data','prop':'terminal_type_data','type':'enum','values':H323_TERMINAL_TYPE_ENUM},
        'irq-supported':{'tag':'irq-supported','prop':'is_irq_supported','type':'boolean'},
        'email-id-from-user':{'tag':'email-id-from-user', 'prop':'email-id-from-user'},
        'support-qos-monitoring':{'tag':'support-qos-monitoring','prop':'support_qos_monitoring','type':'boolean'},
        'behind-vbp':{'tag':'behind-vbp','prop':'is_behind_vbp','type':'boolean'},
    }
    
    def __str__(self, *args, **kwargs):
        return "[H323Identity]%s" % (self.h323_alias)

class PlcmSipIdentity(Plcm):
    root_element = None
    
class PlcmIsdnIdentity(Plcm):
    root_element = None
    

class PlcmDevice(Plcm):
    root_element = "plcm-device"
    target_namespace = "urn:com:polycom:api:rest:plcm-device"
    imported_namespaces = [
        'urn:com:polycom:api:rest:plcm-service-class',
        'urn:com:polycom:api:rest:plcm-h323-identity',
        'urn:com:polycom:api:rest:plcm-isdn-identity',
        'urn:com:polycom:api:rest:plcm-sip-identity',
        'urn:com:polycom:api:rest:plcm-mcu-identity',
        'urn:com:polycom:api:rest:plcm-device-status'
    ]
    element_properties={
        'device-identifier':{'tag':'device-identifier', 'prop':'device_identifier'},
        'plcm-mcu-identity':{'tag':'plcm-mcu-identity','prop':'mcu_identity','type':'urn:com:polycom:api:rest:plcm-mcu-identity','class':PlcmMcuIdentity},
        'plcm-sip-identity':{'tag':'plcm-sip-identity','prop':'sip_identity','type':'urn:com:polycom:api:rest:plcm-sip-identity','class':PlcmSipIdentity},
        'plcm-isdn-identity':{'tag':'plcm-isdn-identity','prop':'isdn_identity','type':'urn:com:polycom:api:rest:plcm-isdn-identity','class':PlcmIsdnIdentity},
        'plcm-h323-identity':{'tag':'plcm-h323-identity','prop':'h323_identity','type':'urn:com:polycom:api:rest:plcm-h323-identity','class':PlcmH323Identity},
        'device-name':{ 'tag':'device-name', 'prop':'device_name'},
        'device-owner':{ 'tag':'device-owner', 'prop':'device_owner'},
        'owner-domain':{ 'tag':'owner-domain', 'prop':'owner-domain'},
        'device-model':{ 'tag':'device-model', 'prop':'device_model'},
        'device-version':{ 'tag':'device-version', 'prop':'device_version'},
        'registration-identifier':{ 'tag':'registration-identifier', 'prop':'registration_identifier'},
        'allow-inactivity-deletion':{ 'tag':'allow-inactivity-deletion', 'prop':'allow_inactivity_deletion', 'type':'boolean'},
        'registration-direction':{ 'tag':'registration-direction', 'prop':'registration_direction'},
        'supports-h323':{ 'tag':'supports-h323', 'type':'boolean', 'prop':'supports_h323'},
        'supports-isdn':{ 'tag':'supports-isdn', 'type':'boolean', 'prop':'supports_isdn'},
        'supports-sip':{ 'tag':'supports-sip', 'type':'boolean', 'prop':'supports_sip'},
        'has-mcu-capabilities':{ 'tag':'has-mcu-capabilities', 'type':'boolean', 'prop':'has_mcu_capabilities'},
        'ip-address':{ 'tag':'ip-address', 'prop':'ip_address'},
        'area-identifier':{ 'tag':'area-identifier', 'prop':'aera_identifier'},
        'scheduler-device':{ 'tag':'scheduler-device', 'type':'boolean', 'prop':'scheduler_device'},
        'passback':{ 'tag':'passback', 'prop':'passback'},
        'passthru':{ 'tag':'passthru', 'prop':'passthru'},
        'entity-tag':{ 'tag':'entity-tag', 'prop':'entity_tag'},
        'device-type':{ 'tag':'device-type', 'prop':'device_type'},
        'manage-mode':{ 'tag':'manage-mode', 'prop':'manage_mode'},
        'serial-number':{ 'tag':'serial-number', 'prop':'serial_number'},
        'site':{ 'tag':'site', 'prop':'site'},
        'plcm-device-status':{'tag':'plcm-device-status','prop':'plcm_device_status','type':'urn:com:polycom:api:rest:plcm-device-status','class':PlcmDeviceStatus}
    }

    def __init__(self, device_name=None):
        self.device_name = device_name
    
    def xml_build_content(self, xml_root):
        xml_root = self.xml_build_from_properties(xml_root)
        
        return xml_root
            
    def get_device_identifier(self):
        return self.xml_source['device-identifier']
    
    def get_device_name(self):
        return self.name
    
    def __str__(self, *args, **kwargs):
        return "[Device]%s/%s/%s" % (self.device_name, self.device_identifier, self.device_type)
    
    
class PlcmDeviceList(Plcm):
    root_element = 'plcm-device-list'
    target_namespace = "urn:com:polycom:api:rest:plcm-device-list"
    imported_namespaces = [
        'urn:com:polycom:api:rest:plcm-device'
    ]
    element_properties={
        'plcm-device':{'prop':'plcm_devices','tag':'plcm-device','type':'urn:com:polycom:api:rest:plcm-device','class':PlcmDevice,'list':True},
    }
