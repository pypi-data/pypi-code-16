#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
import StringIO
import zipfile
import csv
from ..stubs.plcmdevice import PlcmDevice
from ..wrapper.request import PRPPRequest
from ..wrapper.request import PRPPResponse
from ..stubs.plcmdevice import PlcmDeviceList

class Devices(PRPPRequest):
    '''
    classdocs
    '''

    def __init__(self, server, path="devices"):
        super(Devices,self).__init__(server, path)

    def api_export_inventory(self):
        response = self.get("export-inventory")
        zip_binary = StringIO.StringIO(response.content)
        zf = zipfile(zip_binary)
        return zf.read(zf.filelist[0])

    def api_list_device_types(self):
        return self.get("device-types")
    
    def list(self):
        '''Get the devices list'''
        #GET devices
        try:
            response = PRPPResponse(self.api_get(),PlcmDeviceList,200,'devices.list')
            return response
        except Exception, ex:
            print "[prpp][exception]%s" % ex
            raise ex
    
    def list_inventory(self):
        '''Get the zipped listing of devices...'''
        #GET devices/export-inventory
        list_csv = self.api_export_inventory()
        reader = csv.reader(list_csv.strip().split('\n'), delimiter=',')
        header = None
        liste = []
        for row in reader:
            if header == None:
                header = row
            else:
                device = {}
                for index,cell in enumerate(row):
                    if cell:
                        device[header[index]]=cell.strip()
                liste.append(device)
                #print device['Endpoint Name']
        return liste
        
    def get_device(self,device_identifier):
        '''Load one device'''
        #GET devices/$device_identifier
        if device_identifier != None:
            try:
                response = PRPPResponse(self.get(extra_path=device_identifier),PlcmDevice,200,'devices.get_device')
                return response
            except Exception,ex:
                print "[prpp][exception]%s" % ex
                raise ex
        else:
            raise Exception("device_identifier is missing")



