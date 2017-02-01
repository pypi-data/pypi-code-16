"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ListOfActionableResourcesPage_22
from snapp_email.datacontract.utils import export_dict, fill


class ListOfActionableResourcesPage_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ListOfActionableResourcesPage_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfActionableResourcesPage_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'action'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.actionable.resource.list.page-v5.18+json',
            'Accept': 'application/vnd.4thoffice.actionable.resource.list.page-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfActionableResourcesPage_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, actionableResourceId, size, offset, timeframe=None, reminderType=None, impersonate_user_id=None, accept_type=None):
        """
        Retrieve list of actionable resources.
        
        :param actionableResourceId: 
        :type actionableResourceId: 
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param timeframe: Timeframe for requested reminder list.
            Available values:
            - Pending
            - Today
            - Tomorrow
            - Later
            - Completed
        :type timeframe: String
        
        :param reminderType: Filter by type of reminder.
            Available values:
            - Followup
            - Question
            - Mention
            - Calendar
            - Appointment
            - ResponsePending
            - Reminder
        :type reminderType: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfActionableResourcesPage_22
        """
        url_parameters = {
            'timeframe': timeframe,
            'reminderType': reminderType,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
            'actionableResourceId': actionableResourceId,
        }
        endpoint = 'action'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.actionable.resource.list.page-v5.18+json',
            'Accept': 'application/vnd.4thoffice.actionable.resource.list.page-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfActionableResourcesPage_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
