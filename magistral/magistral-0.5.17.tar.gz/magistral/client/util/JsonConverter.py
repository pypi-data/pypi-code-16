'''
Created on 9 Aug 2016

@author: rizarse
'''

import json
import logging
from magistral.client.perm.PermMeta import PermMeta
from magistral.client.Configs import Configs

class JsonConverter(object):
    
    logger = logging.getLogger(__name__)
    
    @staticmethod
    def connectionSettings(_json):
        parsedJson = json.loads(_json)
        
        settings = {}
        pub = {}
        sub = {}
        
        token = ""
        
        for entry in parsedJson:
            
            if entry["producer"] != None: 
                pp = Configs.producerConfigs();
                pp["bootstrap_servers"] = entry["producer"];
                
                if "plain" in pub:
                    pub["plain"].append(pp);
                else:
                    pub["plain"] = [pp]
                
            if entry["producer-ssl"] != None: 
                pp = Configs.producerConfigs();
                pp["bootstrap_servers"] = entry["producer-ssl"];               
                
                if "ssl" in pub:
                    pub["ssl"].append(pp);
                else:
                    pub["ssl"] = [pp]
                
            if entry["consumer"] != None: 
                sp = {}
                sp["bootstrap_servers"] = entry["consumer"];
                
                if "plain" in sub:
                    sub["plain"].append(sp);
                else:
                    sub["plain"] = [sp]
                
            if entry["consumer-ssl"] != None: 
                sp = {}
                sp["bootstrap_servers"] = entry["consumer-ssl"];
                                
                if "ssl" in sub:
                    sub["ssl"].append(sp);
                else:
                    sub["ssl"] = [sp]
            
            if entry["token"] != None:
                token = entry["token"] 
                settings["meta"] = { "token" : entry["token"] }
          
            if entry["ts"] != None:
                settings["ts"] = entry["ts"]
                
            if entry["ks"] != None:
                settings["ks"] = entry["ks"]
        
        settings["pub"] = pub;
        settings["sub"] = sub;        
        
        JsonConverter.logger.debug("Token = %s", token)
        return settings 
    
    @staticmethod
    def __convertPerm(entry):
        permissions = {}

        read = entry["read"];
        write = entry["write"];
        channels = entry["channels"];
                
        if isinstance(channels, list):
            for ch in channels:
                permissions[int(ch)] = (read, write)                     
        else:
            permissions[int(channels)] = (read, write)
        
        return permissions;
    
    @staticmethod
    def userPermissions(_json):
        if (_json == None or _json == 'null'): return [];
                
        parsedJson = json.loads(_json)
        
        permissions = [];
                
        ps = parsedJson["permission"]
        
        if isinstance(ps, list):
            for p in ps: 
                permissions.append(PermMeta(p["topic"], JsonConverter.__convertPerm(p)))
        else:            
            permissions.append(PermMeta(ps["topic"], JsonConverter.__convertPerm(ps)))
                        
        return permissions