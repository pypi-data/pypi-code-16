#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
from .plcm import Plcm

DIAL_DIRECTION_ENUM = {
    'DIAL_OUT' : 'DIAL_OUT',
    'DIAL_IN' : 'DIAL_IN'
}
CONNECTION_TYPE_ENUM={
    'H323':'H323',
    'SIP':'SIP',
    'ISDN':'ISDN',
    'H323_E164':'H323_E164',
    'H323_ANNEX_O':'H323_ANNEX_O',
    'H323_ID':'H323_ID'
}
USER_TYPE_ENUM={
    'USER':'USER',
    'ROOM':'ROOM',
    'GUEST':'GUEST',
    'GUESTBOOK':'GUESTBOOK',
}
MODE_ENUM={
    'IN_PERSON':'IN_PERSON',
    'AUDIO':'AUDIO',
    'VIDEO':'VIDEO'
}
BIT_RATE_ENUM={
    'RATE96':'RATE96',
    'RATE128':'RATE128',
    'RATE192':'RATE192',
    'RATE256':'RATE256',
    'RATE320':'RATE320',
    'RATE384':'RATE384',
}

class PlcmReservedParticipant(Plcm):
    
    root_element = "plcm-reserved-participant"
    target_namespace = "urn:com:polycom:api:rest:plcm-reserved-participant"
    imported_namespaces = None
    element_properties={
        'username': { 'prop':'username','tag':'username' },
        'domain': { 'prop':'domain','tag':'domain' },
        'participant-name': { 'prop':'participant_name','tag':'participant-name','mandatory':True },
        'connection-type-enum': { 'prop':'connection_type','tag':'connection-type-enum', 'type':'enum', 'values':CONNECTION_TYPE_ENUM },
        'dial-direction-enum': { 'prop':'dial_direction','tag':'dial-direction-enum','type':'enum', 'values':DIAL_DIRECTION_ENUM },
        'dial-number': { 'prop':'dial_number','tag':'dial-number' },
        'is-chair': { 'prop':'is_chair','tag':'chairperson', 'type':'boolean','mandatory':True },
        'conf-owner': { 'prop':'is_conf_owner','tag':'conf-owner', 'type':'boolean','mandatory':True },
        'email-address': { 'prop':'email_address','tag':'email-address' },
        'user-type-enum': { 'prop':'user_type','tag':'user-type-enum', 'type':'enum', 'values':USER_TYPE_ENUM },
        'mode-enum': { 'prop':'mode','tag':'mode-enum', 'type':'enum', 'values':MODE_ENUM },
        'bit-rate-enum': { 'prop':'bit_rate','tag':'bit-rate-enum', 'type':'enum', 'values':BIT_RATE_ENUM },
        'device-id': { 'prop':'device_id','tag':'device-id' },
    }
    username=None
    domain=None
    participant_name=None
    connection_type=None
    dial_direction=None
    dial_number=None
    is_chair=None
    is_conf_owner=None
    email_address=None
    user_type=None
    mode=None
    bit_rate=None
    device_id=None
    
    
    def __init__(self, 
                 username=None,
                 domain=None,
                 participant_name=None,
                 connection_type=None,
                 dial_direction=None,
                 dial_number=None,
                 is_chair=False,
                 is_conf_owner=False,
                 email_address=None,
                 user_type=None,
                 mode=None,
                 bit_rate=None,
                 device_id=None):
        self.username = username
        self.domain = domain
        self.participant_name = participant_name
        self.connection_type = connection_type
        self.dial_direction = dial_direction
        self.dial_number = dial_number
        self.is_chair = is_chair
        self.is_conf_owner = is_conf_owner
        self.email_address=email_address
        self.user_type=user_type
        self.mode=mode
        self.bit_rate=bit_rate
        self.device_id=device_id
        
    def __str__(self):
        return "[Participant]%s\%s:%s[%s/%s]" % (self.user_type,self.username,self.participant_name,self.dial_direction,self.dial_number)
    
    def xml_build_content(self, xml_root, nsmap=None):
        if nsmap is not None:
            nsmap = self.xml_populate_nsmap(existing_nsmap=nsmap)
        
        xml_root = self.xml_build_from_properties(xml_root, nsmap)
        return xml_root
    