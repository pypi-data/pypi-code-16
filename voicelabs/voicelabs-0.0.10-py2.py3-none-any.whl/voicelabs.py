'''
Created on Sep 18, 2016
modified on Feb 11, 2016
@author: sridharn
'''
import sys
import json
import requests
import hashlib
import logging
import traceback

class VoiceInsights:
    
    appToken = ''
    session = None
        
    def sendVLEvent(self, payload):
        url = "https://api.voicelabs.co/events"
        params = { "auth_token" : payload['app_token']}
        data_json = json.dumps(payload)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, params=params, data=data_json, headers=headers, timeout=1)
        return response


    def md5(self, input_string):
        return hashlib.md5(input_string.encode('utf-8')).hexdigest()

            
    def __init__(self):
        pass
    
    def getBasestring(self):
        if (sys.version_info > (3, 0)):
            return (str, bytes)
        else:
            return basestring

    def initialize(self, appToken, session):
        
        try:
            if session is None or appToken is None or len(appToken.strip()) == 0:
                logging.error("ERROR: cannot initialize VoiceInsights SDK. either session or appToken are 'None'")
                return

            if 'userId' not in session.get('user',{}):
                logging.error("ERROR: cannot initialize VoiceInsights SDK. User Id is not found in session")
                return
                
            if 'sessionId' not in session:
                logging.error("ERROR: cannot initialize VoiceInsights SDK. sessionId is not found in session")
                return
                
            if self.session is not None and self.session['sessionId'] == session['sessionId']:
                # logging.error("WARNING: Redundant Initialization. A session has already been started with sessionId: %s", session['sessionId'])
                return

            self.appToken = appToken
            self.session = session
            p =  {}
            p['app_token'] = self.appToken
            p['user_hashed_id'] = self.md5(self.session['user']['userId'])
            p['session_id'] = self.session['sessionId'];
            p['event_type'] = 'INITIALIZE'
            p['data'] = None
            resp = self.sendVLEvent(p)
            return resp

        except:
            logging.error("ERROR: occurred inside initalize")
            traceback.print_exc()
            return None


    def track(self, intent_name, intent_request, response):
    
        try:    
            if self.session is None:
                logging.error("ERROR: Voice Insights has not been initialized. Initalize() method need to have been invoked before tracking")
                return
                  
            p =  {}
            p['app_token'] = self.appToken
            p['user_hashed_id'] = self.md5(self.session['user']['userId'])
            p['session_id'] = self.session['sessionId'];
            p['event_type'] = 'SPEECH'
            p['intent'] = intent_name
            p['data'] = {}

            if intent_request is not None and 'slots' in intent_request.get('intent',{}):
                p['data']['metadata'] = intent_request['intent']['slots']
            else:
                p['data']['metadata'] = None
            
            vl_basestring = None

            # if (sys.version_info > (3, 0)):
            #     vl_basestring = (str, bytes)
            # else:
            #     vl_basestring = basestring

            if isinstance(response, self.getBasestring()):
                p['data']['speech'] = response

            elif response is not None and 'response' in response and 'outputSpeech' in response.get('response', {}):
                speechObj = response['response']['outputSpeech']

                if 'type' in speechObj:
                    if speechObj['type'] == 'SSML':
                        p['data']['speech'] = response['response']['outputSpeech']['ssml']
                    elif speechObj['type'] == 'PlainText':
                        p['data']['speech'] = response['response']['outputSpeech']['text']
                    else:
                        logging.error("ERROR: passed a response object with an unknown Type") 
                else:
                    logging.error("ERROR: passed a response object thats not an Alexa response") 

            else:
                p['data']['speech'] = None

            resp = self.sendVLEvent(p)             
            return resp

        except:
            logging.error("ERROR: occurred inside track method")
            traceback.print_exc()
            return None