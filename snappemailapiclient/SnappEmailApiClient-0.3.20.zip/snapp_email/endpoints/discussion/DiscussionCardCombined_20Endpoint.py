"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import DiscussionCardCombined_20
from snapp_email.datacontract.utils import export_dict, fill


class DiscussionCardCombined_20Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'DiscussionCardCombined_20'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: DiscussionCardCombined_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'discussion'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.discussion.card.combined-5.15+json',
            'Accept': 'application/vnd.4thoffice.discussion.card.combined-5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(DiscussionCardCombined_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, cardId, size, offset, htmlFormat=None, returnForwardedCopyPosts=None, impersonate_user_id=None, accept_type=None):
        """
        Retrieve discussion card resource.
        
        :param cardId: 
        :type cardId: 
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param htmlFormat: Mime format for html body of post resource.
            Available values:
            - text/html-stripped
            - text/html-stripped.mobile
        :type htmlFormat: String
        
        :param returnForwardedCopyPosts: Return copied posts on forwarded discussion card.
        :type returnForwardedCopyPosts: Boolean
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: DiscussionCardCombined_20
        """
        url_parameters = {
            'htmlFormat': htmlFormat,
            'returnForwardedCopyPosts': returnForwardedCopyPosts,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
            'cardId': cardId,
        }
        endpoint = 'discussion/{cardId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.discussion.card.combined-5.15+json',
            'Accept': 'application/vnd.4thoffice.discussion.card.combined-5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(DiscussionCardCombined_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
