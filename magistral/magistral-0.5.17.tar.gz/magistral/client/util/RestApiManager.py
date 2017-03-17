'''
Created on 9 Aug 2016

@author: rizarse
'''

import requests
import logging
from magistral.client.MagistralException import MagistralException
# from magistral.client.MagistralExceptionType import MagistralExceptionType

class RestApiManager:        
   
    logging.basicConfig(level = logging.DEBUG);    
    logger = logging.getLogger(__name__);

    @staticmethod
    def get(path, params = None, user = None, password = None, callback = None):
        
        log = RestApiManager.logger;
        log.debug("HTTP GET: %s %s %s %s", path, params, user, password)
        
        r = None;
        
        if params == None:
            if user == None or password == None:
                r = requests.get(path);
            else:
                r = requests.get(path, auth=(user, password));
        else:
            if user == None or password == None:
                r = requests.get(path, params=params);
            else:
                s = requests.Session()
                s.auth = (user, password)
                s.params = params
                
                r = s.get(path);
        
        if r != None:
            if (r.ok):
                log.debug("JSON: %s", r.text);
                if (callback != None): callback(r.text, None);
                return r.text;                
            else:            
                log.error("ERROR: [%d] %s", r.status_code, r.text, r.content);
                if (callback != None): callback(r.text, MagistralException(r.text));
                return None;            
        else:
            log.error("ERROR: %S", r.text);
            if (callback != None): callback(None, MagistralException(r.text)); 
            return None;
        
    @staticmethod
    def put(path, params = None, user = None, password = None, callback = None):
        
        log = RestApiManager.logger;
        log.debug("HTTP PUT: %s %s %s %s", path, params, user, password)
        
        r = None;
        
        if params == None:
            if user == None or password == None:
                r = requests.put(path);
            else:
                r = requests.put(path, auth=(user, password));
        else:
            if user == None or password == None:
                r = requests.put(path, params=params);
            else:
                s = requests.Session()
                s.auth = (user, password)
                s.params = params
                
                r = s.put(path);
        
        if r != None:
            if (r.ok):
                log.debug("JSON: %s", r.text);
                if (callback != None): callback(r.text, None);
                return r.text;              
            else:            
                log.error("ERROR: [%d] %s", r.status_code, r.text, r.content);
                if (callback != None): callback(r.text, MagistralException(r.text));   
                return None;         
        else:
            log.error("ERROR: %S", r.text);
            if (callback != None): callback(None, MagistralException(r.text));
            return None;
            
    @staticmethod
    def delete(path, params = None, user = None, password = None, callback = None):
        
        log = RestApiManager.logger;
        log.debug("HTTP PUT: %s %s %s %s", path, params, user, password)
        
        r = None;
        
        if params == None:
            if user == None or password == None:
                r = requests.delete(path);
            else:
                r = requests.delete(path, auth=(user, password));
        else:
            if user == None or password == None:
                r = requests.delete(path, params=params);
            else:
                s = requests.Session()
                s.auth = (user, password)
                s.params = params
                
                r = s.delete(path);
        
        if r != None:
            if (r.ok):
                log.debug("JSON: %s", r.text);
                if (callback != None): callback(r.text, None);  
                return r.text;              
            else:            
                log.error("ERROR: [%d] %s", r.status_code, r.text, r.content);
                if (callback != None): callback(r.text, MagistralException(r.text));   
                return None;         
        else:
            log.error("ERROR: %S", r.text);
            if (callback != None): callback(None, MagistralException(r.text)); 
            return None;
        