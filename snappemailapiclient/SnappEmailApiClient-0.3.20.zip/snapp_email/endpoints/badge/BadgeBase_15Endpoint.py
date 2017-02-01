"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import BadgeBase_15
from snapp_email.datacontract.utils import export_dict, fill


class BadgeBase_15Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'BadgeBase_15'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: BadgeBase_15
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'badge'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.badge-5.0+json',
            'Accept': 'application/vnd.4thoffice.badge-5.0+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(BadgeBase_15, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def delete(self, feedscope, feedidentity=None, impersonate_user_id=None, accept_type=None):
        """
        Clear badge count.
        
        :param feedscope: Specify feed scope.
            Available values:
            - All
            - Stream
            - ChatStream
            - Card
            - Post
        :type feedscope: FeedScope
        
        :param feedidentity: Specify feed id.
        :type feedidentity: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: True if object was deleted, otherwise an exception is raised
        :rtype: bool
        """
        url_parameters = {
            'feedscope': feedscope,
            'feedidentity': feedidentity,
        }
        endpoint_parameters = {
        }
        endpoint = 'badge'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.badge-5.0+json',
            'Accept': 'application/vnd.4thoffice.badge-5.0+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('delete', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return True
