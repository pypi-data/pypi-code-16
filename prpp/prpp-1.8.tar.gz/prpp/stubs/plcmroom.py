#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
from .plcm import Plcm
from .plcmdevice import PlcmDevice

class PlcmRoom(Plcm):
    
    root_element = "plcm-room"
    target_namespace = "urn:com:polycom:api:rest:plcm-room"
    imported_namespaces = [
        'http://www.w3.org/2005/Atom',
        'urn:com:polycom:api:rest:plcm-device',
    ]
    element_properties={
        'room-uuid':{'prop':'room_uuid','tag':'room-uuid'},
        'roomname':{'prop':'roomname', 'tag':'roomname'},
        'domain':{'prop':'domain','tag':'domain'},
        'email-address':{'prop':'email_address','tag':'email-address'},
        'description':{'prop':'description','tag':'description'},
        'tenant-id':{'prop':'tenant_id','tag':'tenant-id'},
        'site-uuid':{'prop':'site_uuid','tag':'site-uuid'},
        'site-name':{'prop':'site_name','tag':'site-name'},
        'entity-tag':{'prop':'entity_tag','tag':'entity-tag'},
        'associated-device':{'prop':'associated_device','tag':'associated-device','type':'urn:com:polycom:api:rest:plcm-device','class':PlcmDevice,'list':True}
    }
    room_uuid = None
    roomname = None
    domain = None
    email_address = None
    description = None
    tenant_id = None
    site_uuid = None
    site_name = None
    entity_tag = None
    associated_device = None

    def __init__(self, plcm_device=None):
        self.device = plcm_device
        
    def xml_build_content(self, xml_root):
        xml_root = self.xml_build_from_properties(xml_root)
        
        if self.device:
            xml_root.append(self.device.xml_build(build_nsmap=True,nsmap=xml_root.nsmap))

        return xml_root
    
    def __str__(self):
        return "[Room]%s{%s}@%s\%s" % (self.roomname,self.room_uuid,self.domain,self.site_name)
    
    
class PlcmRoomList(Plcm):
    root_element = "plcm-room-list"
    target_namespace = "urn:com:polycom:api:rest:plcm-room-list"
    imported_namespaces = [
        'urn:com:polycom:api:rest:plcm-room',
    ]
    element_properties={
        'plcm-room':{'prop':'plcm_rooms','tag':'plcm-room','type':'urn:com:polycom:api:rest:plcm-room','class':PlcmRoom,'list':True},
    }
    