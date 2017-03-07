#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
from ..wrapper.request import PRPPRequest
from lxml import etree
from ..wrapper.request import PRPPResponse

class Users(PRPPRequest):
    
    def __init__(self, server, path="users"):
        super(Users,self).__init__(server, path)

    def list(self):
        try:
            response = PRPPResponse(self.get(),PlcmUser,200,'users.list')
            return response
        except Exception,ex:
            print "[prpp][exception]%s" % ex