#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from ..stubs.plcmerror import PlcmError
from lxml import etree

class PRPPResponse(object):
    #Requests response based uppon
    response=None
    #Attended success code
    success_code=None
    #lxml parsed representation
    xml=None
    #Plcm class attended
    plcm_class=None
    #Plcm instance passed to send
    plcm_in=None
    #Plcm object received from server
    plcm_out=None
    #Redirection to load 
    plcm_redirect=None
    #Plcm error received from server
    plcm_error=None
    #Library error
    error=None
    #Is instance's object still building by caller
    building=False
    #Label of instance caller
    label=None
    #Allow or not empty response (Location redirect)
    allow_empty_response=None
    #Extradata
    extra_data=None
    
    def __init__(self, response, plcm_class, success_code, label, plcm_in=None, allow_empty_response=False):
        self.label=label
        self.success_code=success_code
        self.allow_empty_response=allow_empty_response
        if response != None:
            self.building=True
            self.response=response
            self.plcm_class=plcm_class
            self.parse_xml()
            self.parse_plcm_return()
        else:
            raise Exception("Response is None for %s" % self.label)
        
    def load_plcm(self,response, plcm_class, success_code, label):
        #print 
        self.label = label
        self.success_code = success_code
        if response != None:
            self.response = response
            self.plcm_class = plcm_class
            self.parse_xml()
            self.parse_plcm_return()
        else:
            raise Exception("Response is None for %s" % self.label)
        
    def parse_xml(self):
        '''Try to parse response.content with lxml lib'''
        if self.allow_empty_response==True and self.is_content_empty():
            return
        
        try:
            self.xml = etree.fromstring(self.response.content)
        except Exception,ex:
            print "[prpp][exception]%s" % ex
            self.error = "Can't parse XML received for %s %s %s" % (self.label,self.allow_empty_response, self.response.content)
    
    def parse_plcm_return(self):
        if self.response.status_code==500:
            raise Exception("Server error 500")
        if self.response.status_code != self.success_code:
            #Error
            if self.allow_empty_response==True and self.is_content_empty():
                return 
            else:
                self.plcm_error = PlcmError().xml_parse(self.xml)
        else:
            #Redirection to element concerned
            if 'location' in self.response.headers:
                self.plcm_redirect = self.response.headers['location']
            elif 'recurrence-id' in self.response.headers:
                self.plcm_redirect = self.response.headers['recurrence-id']
            else:
                if self.allow_empty_response==True and self.is_content_empty():
                    return
                else:
                    self.plcm_out = self.plcm_class().xml_parse(self.xml)
    
    def is_content_empty(self):
        return len(self.response.content)==0
    
    def get_error(self):
        if self.plcm_error!=None:
            return self.plcm_error
        else:
            return self.error
    
    def is_done(self):
        '''Must be called in order to indicate that instance is build'''
        self.building=False
        
    def __str__(self, *args, **kwargs):
        return '[PRPPResponse]%s\%s(%s)' % (self.building,self.get_error(),self.label)

class PRPPRequest(object):
    server = None
    path = None
    
    def __init__(self, server, path):
        self.server = server
        self.path = path
    
    def get(self, extra_path=None, query_params=None):
        '''
        Make a get http request to the server
        '''
        url = self.server.url
        if self.path:
            url = "%s/%s" % (url, self.path)
        if extra_path:
            url = "%s/%s" % (url, extra_path)
            
        print("[prpp]GET %s %s" % (url,query_params));
        try:
            response = requests.get(url,
                                verify=False,
                                auth=self.server.httpBasicAuth,
                                params = query_params)
            #PRPPRequest.pretty_print(response.request)
            print "[prpp]%s/%s" % (response.status_code,response.headers)
            #print "[prpp] %s " % response.content
            return response
        except Exception, ex:
            print "[prpp][exception]%s" % ex
            return None

    def post(self, plcm, extra_path=None):
        url = self.server.url
        if self.path:
            url = "%s/%s" % (url, self.path)
        if extra_path:
            url = "%s/%s" % (url, extra_path)
            
        print("[prpp]POST %s" % url);
        print("[prpp]XML %s" % plcm.xml_tostring());
        try:
            response = requests.post(url,
                                data=plcm.xml_tostring(),
                                headers = { 'Content-Type':plcm.get_content_type() },
                                verify=False,
                                auth=self.server.httpBasicAuth,
                                allow_redirects=True)
            print "[prpp]%s/%s" % (response.status_code,response.headers)
            #print response.content
            return response
        except Exception, ex:
            print "[prpp][exception]%s" % ex
            return None

    def put(self, plcm, extra_path=None):
        url = self.server.url
        if self.path:
            url = "%s/%s" % (url, self.path)
        if extra_path:
            url = "%s/%s" % (url, extra_path)
            
        print("[prpp]PUT %s" % url);
        print("[prpp]XML %s" % plcm.xml_tostring());
        try:
            response = requests.put(url,
                                data=plcm.xml_tostring(),
                                headers = { 'Content-Type':plcm.get_content_type() },
                                verify=False,
                                auth=self.server.httpBasicAuth,
                                allow_redirects=True)
            print "[prpp]%s/%s" % (response.status_code,response.headers)
            #print response.content
            return response
        except Exception, ex:
            print "[prpp][exception]%s" % ex
            return None
        
    def delete(self, extra_path=None):
        url = self.server.url
        if self.path:
            url = "%s/%s" % (url, self.path)
        if extra_path:
            url = "%s/%s" % (url, extra_path)
            
        print("[prpp]DELETE %s" % url);
        try:
            response = requests.delete(url,
                                verify=False,
                                auth=self.server.httpBasicAuth,
                                allow_redirects=True)
            print "[prpp]%s/%s" % (response.status_code,response.headers)
            #print response.content
            return response
        except Exception, ex:
            print "[prpp][exception]%s" % ex
            return None

    def api_get(self):
        response = self.get()
        return response
    
    def parseResponse(self):
        response = self.get()
        
    def parseLinks(self, xml):
        return None
    
    def canConnect(self):
        return self.get() != None
    
    @staticmethod
    def pretty_print(req):
        print('{}\n{}\n{}\n\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    
    
