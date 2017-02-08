# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

import requests
import json
from requests.exceptions import (
    ConnectionError, ConnectTimeout, InvalidSchema, InvalidURL,
    MissingSchema, ReadTimeout, Timeout, RequestException, RetryError, TooManyRedirects,
    ProxyError)
from tabulate import tabulate
from fdscli.model.fds_error import FdsError
from fdscli.services.fds_auth_error import FdsAuthError

class RESTHelper():
    
    AUTH_FAILED = "Authentication Failed."
    
    def __init__(self):
        return
    
    def buildHeader(self, session):
        
        t = session.get_token()
        
        return { "FDS-Auth" : t }   
        
    def defaultSuccess(self, response):
    
        print("\n")
        
        if ( len(response) == 0 ):
            return
        else:
            print(tabulate( response, "keys" ))
            print("\n")
    
    def defaultErrorHandler(self, error):
        
        errorText = "";
        err_message = str(error.status_code) + ": "
        
        try:
            errorText = json.loads( error.text )
        except ValueError:
            #do nothing and go on
            pass
        
        if "message" in errorText:
            err_message += errorText["message"]
        else:
            err_message += error.reason
        
        if error.status_code == 404:
            err_message = "The operation received a 404 response, this means there is a problem communicating with the FDS cluster."

        if error.status_code == requests.codes.service_unavailable:
            error_message = ("The server is currently unable to handle the request. "
                "This is a temporary condition which will be alleviated after some delay.")

        print(err_message)
        
        return err_message
            
    def post(self, session, url, data=None, successCallback=defaultSuccess, failureCallback=defaultErrorHandler):
        '''
        Returns
        -------
        object: json-encoded content of a response, if any; type depends on JSON Document deserialization
        '''
        
        try:
            header = self.buildHeader(session)
        except FdsAuthError as fae:
            return FdsError( error=fae.error_code, message=fae.message)

        response = requests.Response()

        try:
            response = requests.post( url, data=data, headers=header, verify=False, timeout=(10, 31))
        except ConnectTimeout as errConnectTimeout:
            response.status_code = 408
            response.reason = errConnnectTimeout.message.message
        except ReadTimeout as errReadTimeout:
            response.status_code = 408
            response.reason = errReadTimeout.message.message
        except RequestException as ex:
            response.status_code = 500
            response.reason = ex.message.message

        if ( response.ok is False ):
            message = failureCallback( self, response )
            return FdsError( error=response, message=message )

        # In case the JSON decoding fails, response.json raises an exception. For example, if the
        # response gets a 204 (No Content), or if the response contains invalid JSON, attempting
        # response.json raises ValueError: No JSON object could be decoded.
        rj = None
        try:
            # For code 202 Accepted, the entity returned with the response SHOULD include an
            # indication of the request's current status and either a pointer to a status monitor
            # or some estimate of when the user can expect the request to be fulfilled.
            rj = response.json()
        except ValueError:
            d = dict()
            d["code"] = response.status_code
            if ( response.status_code == requests.codes.accepted ):
                d["description"] = "accepted"
            rj = json.dumps(d)

        return rj

    def put(self, session, url, data=None, successCallback=defaultSuccess, failureCallback=defaultErrorHandler):
        '''
        Returns
        -------
        object: json-encoded content of a response, if any; type depends on JSON Document deserialization
        '''
        
        try:
            header = self.buildHeader(session)
        except FdsAuthError as fae:
            return FdsError( error=fae.error_code, message=fae.message)
                
        response = requests.put( url, data=data, headers=header, verify=False )
        
        if ( response.ok is False ):
            message = failureCallback( self, response )
            return FdsError( error=response, message=message )
        
        rj = response.json()
        return rj    
    
    def get(self, session, url, params={}, successCallback=defaultSuccess, failureCallback=defaultErrorHandler):
        '''
        Returns
        -------
        object: json-encoded content of a response, if any; type depends on JSON Document deserialization
        '''

        try:
            header = self.buildHeader(session)
        except FdsAuthError as fae:
            return FdsError( error=fae.error_code, message=fae.message)      

        response = requests.Response()

        try:
            # A time-out of 121 sec is useless from CLI end user perspective. It will effectively
            # appear as a hang. Unfortunately, there are some blocking requests that actually
            # take that long, and system tests fail without a long timeout!
            # TODO: One behavior for SDK mode, another for interactive mode?
            response = requests.get( url, params=params, headers=header, verify=False, timeout=(10, 121))
        except ConnectTimeout as errConnectTimeout:
            response.status_code = 408
            response.reason = errConnnectTimeout.message.message
        except ReadTimeout as errReadTimeout:
            response.status_code = 408
            response.reason = errReadTimeout.message.message
        except RequestException as ex:
            response.status_code = 500
            response.reason = ex.message.message

        if ( response.ok is False ):
            message = failureCallback( self, response )
            return FdsError( error=response, message=message )
        
        rj = response.json()

        return rj
    
    def delete(self, session, url, params={}, successCallback=defaultSuccess, failureCallback=defaultErrorHandler):
        '''
        Returns
        -------
        object: json-encoded content of a response, if any; type depends on JSON Document deserialization
        '''
        
        try:
            header = self.buildHeader(session)
        except FdsAuthError as fae:
            return FdsError( error=fae.error_code, message=fae.message)     
        
        response = requests.delete( url, params=params, headers=header, verify=False)
        
        if ( response.ok is False ):
            message = failureCallback( self, response )
            return FdsError( error=response, message=message )
        
        # In case the JSON decoding fails, response.json raises an exception. For example, if the
        # response gets a 204 (No Content), or if the response contains invalid JSON, attempting
        # response.json raises ValueError: No JSON object could be decoded.
        rj = None
        try:
            # For code 202 Accepted, the entity returned with the response SHOULD include an
            # indication of the request's current status and either a pointer to a status monitor
            # or some estimate of when the user can expect the request to be fulfilled.
            rj = response.json()
        except ValueError:
            d = dict()
            d["code"] = response.status_code
            if ( response.status_code == requests.codes.accepted ):
                d["description"] = "accepted"
            rj = json.dumps(d)

        return rj

