"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import PostActionList_22
from snapp_email.datacontract.utils import export_dict, fill


class PostActionList_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'PostActionList_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: PostActionList_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'post'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.post.action.list-5.18+json',
            'Accept': 'application/vnd.4thoffice.post.action.list-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(PostActionList_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, postId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve post action list resource.
        
        :param postId: 
        :type postId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: PostActionList_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'postId': postId,
        }
        endpoint = 'post/{postId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.post.action.list-5.18+json',
            'Accept': 'application/vnd.4thoffice.post.action.list-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(PostActionList_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
