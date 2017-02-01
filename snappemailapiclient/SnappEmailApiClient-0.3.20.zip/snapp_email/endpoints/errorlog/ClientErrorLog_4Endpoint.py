"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ClientErrorLog_4
from snapp_email.datacontract.utils import export_dict, fill


class ClientErrorLog_4Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ClientErrorLog_4'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ClientErrorLog_4
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'errorlog'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.marg.bcsocial.error.log.client-2.6+json',
            'Accept': 'application/vnd.marg.bcsocial.error.log.client-2.6+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ClientErrorLog_4, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def create(self, obj, impersonate_user_id=None, accept_type=None):
        """
        Post error log from client side.
        
        :param obj: Object to be persisted
        :type obj: ClientErrorLog_4
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ClientErrorLog_4
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'errorlog'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.marg.bcsocial.error.log.client-2.6+json',
            'Accept': 'application/vnd.marg.bcsocial.error.log.client-2.6+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('post', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(ClientErrorLog_4, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
