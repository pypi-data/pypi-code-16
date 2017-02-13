#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of OTC Tool released under MIT license.
# Copyright (C) 2016 T-systems Kurt Garloff, Zsolt Nagy

from otcclient.core.OtcConfig import OtcConfig 
from otcclient.utils import utils_http
from otcclient.utils import utils_http, utils_templates

from otcclient.core.otcpluginbase import otcpluginbase
from otcclient.core.pluginmanager import getplugin
import base64
from time import sleep
import sys
from otcclient.plugins.ecs import ecs
import json
import os
    
class smn(otcpluginbase):
    ar = {}    
    
    @staticmethod
    def otcOutputHandler(): 
        return getplugin(OtcConfig.OUTPUT_FORMAT)
 
    def otctype(self):
        return "func" 


    @staticmethod 
    def list_topics():  
        url = "https://" + OtcConfig.DEFAULT_HOST +  "/v2/" + OtcConfig.PROJECT_ID + "/notifications/topics?offset=0&limit=10"
        
        ret = utils_http.get(url)        
        ecs.otcOutputHandler().print_output(ret, mainkey = "topics", listkey={"name","display_name","topic_urn"})
        maindata = json.loads(ret)
        print maindata['topics'][0]['topic_urn']
        for topic in maindata['topics']:
            topic_subs = smn.list_subscription(topic['topic_urn'])
            ecs.otcOutputHandler().print_output(topic_subs, mainkey = "subscriptions", listkey={"topic_urn","subscription_urn","protocol","endpoint","status"})
            return ret

    @staticmethod 
    def list_subscription(URN=0):  
    #url = "https://iam.eu-de.otctest.t-systems.com/v2/ce91fbb4a862415eb5150eb7f6fa1413/notifications/topics/urn:smn:eu-de:ce91fbb4a862415eb5150eb7f6fa1413:CTS-Test/subscriptions?limit=10&offset=0"
        url = "https://" + OtcConfig.DEFAULT_HOST +  "/v2/" + OtcConfig.PROJECT_ID + "/notifications/topics/urn:smn:eu-de:ce91fbb4a862415eb5150eb7f6fa1413:CTS-Test/subscriptions?offset=0&limit=10"
        if URN is 0:
            URN="urn:smn:eu-de:ce91fbb4a862415eb5150eb7f6fa1413:CTS-Test"    
            url = "https://" + OtcConfig.DEFAULT_HOST +  "/v2/" + OtcConfig.PROJECT_ID + "/notifications/topics/"+URN+"/subscriptions?offset=0&limit=10"
            ret = utils_http.get(url)        
            return ret

    @staticmethod 
    def list_subscriptions():  
    #https://console.otctest.t-systems.com/smn/rest/v2/e60b46f41a2e4e7790b37ab8a425bad6/notifications/topics/urn:smn:eu-de:e60b46f41a2e4e7790b37ab8a425bad6:CTS-TEST/subscriptions?limit=10&offset=0
        url = "https://" + OtcConfig.DEFAULT_HOST +  "/v2/" + OtcConfig.PROJECT_ID + "/notifications/topics?offset=0&limit=10"
        print "PROJECT_ID="+OtcConfig.PROJECT_ID;
        print "URL="+url;
        #url = "https://iam.eu-de.otctest.t-systems.com/v2/ce91fbb4a862415eb5150eb7f6fa1413/notifications/topics/urn:smn:eu-de:ce91fbb4a862415eb5150eb7f6fa1413:CTS-Test/subscriptions?limit=10&offset=0"
        url = "https://" + OtcConfig.DEFAULT_HOST +  "/v2/" + OtcConfig.PROJECT_ID + "/notifications/topics/urn:smn:eu-de:ce91fbb4a862415eb5150eb7f6fa1413:CTS-Test/subscriptions?offset=0&limit=10"
        
        if not OtcConfig.INSTANCE_NAME is None:
            ecs.convertINSTANCENameToId() 

        if OtcConfig.INSTANCE_ID is None: 
            ret = utils_http.get(url)        
            print "RETURN="+ret;
            #ecs.otcOutputHandler().print_output(ret, mainkey = "subscriptions", listkey={"topic_urn","protocol","subscription_urn","owner","endpoint","remark","status"})
            ecs.otcOutputHandler().print_output(ret, mainkey = "subscriptions", listkey={"topic_urn","protocol","subscription_urn","endpoint","status"})
        else:            
            ret = utils_http.get(url + '/' + OtcConfig.INSTANCE_ID )        
            maindata = json.loads(ret)
            if "itemNotFound" in  maindata:
                raise RuntimeError("Not found!")                      
            ecs.otcOutputHandler().print_output(ret,mainkey="server") 
        return ret