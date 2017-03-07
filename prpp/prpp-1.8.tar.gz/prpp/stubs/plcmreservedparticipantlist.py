#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 5 févr. 2016

@author: Adrien
'''
from .plcm import Plcm
from .plcmreservedparticipant import PlcmReservedParticipant
from .plcmroom import PlcmRoom
from .plcmreservedparticipant import USER_TYPE_ENUM

class PlcmReservedParticipantList(Plcm):
    root_element = 'plcm-reserved-participant-list'
    target_namespace = 'urn:com:polycom:api:rest:plcm-reserved-participant-list'
    imported_namespaces = [
        'urn:com:polycom:api:rest:plcm-reserved-participant'
    ]
    element_properties={
        'plcm-reserved-participant':{'prop':'plcm_participants','tag':'plcm-reserved-participant','type':'urn:com:polycom:api:rest:plcm-reserved-participant','class':PlcmReservedParticipant,'list':True},
    }
    plcm_participants=None
    
    def __init__(self):
        self.plcm_participants = []
        
    def __str__(self):
        return "%s(%d)" % ("ReservedParticipantList",len(self.plcm_participants) if hasattr(self,'plcm_participants') else 0)
        
    def add_participant(self,plcm_participant):
        '''Add a participant to the list'''
        self.plcm_participants.append(plcm_participant)
        
    
    def xml_build_content(self, xml_root, nsmap=None):
        '''Build XML representation of this instance'''
        #Parent NSMAP in order to use declared prefix
        #if nsmap is not None:
        #    nsmap = self.xml_populate_nsmap(existing_nsmap=nsmap)
        #    print "NSMAP IS %s" % nsmap
        
        xml_root = self.xml_build_from_properties(xml_root, nsmap)
        return xml_root
    
    def has_participant(self,plcm_item):
        check_room = isinstance(plcm_item, PlcmRoom)
        #check_user plus tard
        for plcm_participant in self.plcm_participants:
            print "[prpp]%s" % plcm_participant
            if check_room==True and plcm_participant.user_type == USER_TYPE_ENUM['ROOM']:
                    if plcm_participant.participant_name.strip() == plcm_item.roomname.strip():
                        return True
        return False