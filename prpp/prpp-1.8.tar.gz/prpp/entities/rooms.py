#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
from lxml import etree
from ..stubs.plcmroom import PlcmRoom
from ..wrapper.request import PRPPRequest
from ..wrapper.request import PRPPResponse
from ..stubs.plcmroom import PlcmRoomList
from prpp.stubs.plcm import PlcmStringList

class Rooms(PRPPRequest):

    def __init__(self, server, path="rooms"):
        super(Rooms,self).__init__(server, path)
    
    def api_get(self, room_uuid):
        if room_uuid:
            return self.get(extra_path=room_uuid)
        else:
            return None

    def list(self, site_uuid=None, limit=None):
        #GET rooms
        try:
            response = PRPPResponse(self.get(query_params={}),
                                    PlcmRoomList,
                                    200,
                                    'rooms.list')
            response.is_done()
            return response
        except Exception,ex: 
            print "[prpp][exception]%s" % ex
            raise ex

    def create_room(self):
        #POST rooms
        raise NotImplementedError
        
    def get_room(self, room_uuid):
        '''Load specific room from server'''
        #GET rooms/{room_uuid}
        if room_uuid!=None:
            try:
                response = PRPPResponse(self.api_get(room_uuid),PlcmRoom,200,'rooms.get')
                response.is_done()
                return response
            except Exception,ex:
                print "[prpp][exception]%s" % ex
                raise ex
        else:
            raise Exception("room_uuid is missing")
        
    def get_associated_devices(self,room_uuid):
        """ Load associated devices of a room """
        #GET rooms/{room_uuid}
        if room_uuid!=None:
            try:
                response = PRPPResponse(self.api_get("%s/associated-devices" % room_uuid),PlcmStringList,200,'rooms.get_associated_devices')
                response.is_done()
                return response
            except Exception,ex:
                print "[prpp][exception]%s" % ex
                raise ex
        else:
            raise Exception("room_uuid is missing")
    
    def delete_room(self, room_uuid):
        #POST rooms/{room_uuid}
        raise NotImplementedError
    
    def update_room(self, PlcmRoom):
        #PUT rooms/{room_uuid}
        raise NotImplementedError
    
    def list_devices(self, room_uuid):
        #GET rooms/{room_uuid}/associated_devices
        raise NotImplementedError
    
    def associate_device(self,room_uuid,PlcmDevice):
        #POST rooms/{room_uuid}/associated_devices
        raise NotImplementedError

