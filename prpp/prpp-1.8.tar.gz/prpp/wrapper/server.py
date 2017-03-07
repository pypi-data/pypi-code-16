#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 1 févr. 2016

@author: Adrien
'''
from requests.auth import HTTPBasicAuth
from .request import PRPPRequest

class PolycomServer(object):
    '''
    classdocs
    '''
    address = None
    protocol = None
    port = None
    url = None
    username = None
    password = None
    path = None
    httpBasicAuth = None

    def __init__(self, address,username, password, protocol="https", port="8443", path="api/rest"):
        '''
        Constructor
        '''
        self.address = address
        self.protocol = protocol
        self.port = port
        self.path = path
        self.url = self.buildUrl()
        self.username = username
        self.password = password
        self.httpBasicAuth = HTTPBasicAuth(username,password)

    def buildUrl(self):
        return "%s://%s:%s/%s" % (self.protocol, self.address, self.port, self.path)
    
    def test_connection(self):
        print PRPPRequest(self, "users").api_get()
        
    def __str__(self, *args, **kwargs):
        return "[PolycomServer]%s" % self.buildUrl()
