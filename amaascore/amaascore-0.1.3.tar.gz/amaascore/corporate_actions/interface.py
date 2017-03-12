import requests

from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface
from amaascore.corporate_actions.utils import json_to_corporate_action


class CorporateActionsInterface(Interface):

    def __init__(self):
        endpoint = ENDPOINTS.get('corporate_actions')
        super(CorporateActionsInterface, self).__init__(endpoint=endpoint)

    def new(self, corporate_action):
        url = self.endpoint + '/corporate_actions'
        response = requests.post(url, json=corporate_action.to_interface())
        if response.ok:
            corporate_action = json_to_corporate_action(response.json())
            return corporate_action
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def amend(self, corporate_action):
        url = '%s/corporate_actions/%s/%s' % (self.endpoint, corporate_action.asset_manager_id,
                                              corporate_action.corporate_action_id)
        response = requests.put(url, json=corporate_action.to_interface())
        if response.ok:
            corporate_action = json_to_corporate_action(response.json())
            return corporate_action
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve(self, asset_manager_id, corporate_action_id):
        url = '%s/corporate_actions/%s/%s' % (self.endpoint, asset_manager_id, corporate_action_id)
        response = requests.get(url)
        if response.ok:
            return json_to_corporate_action(response.json())
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def cancel(self, asset_manager_id, corporate_action_id):
        url = '%s/corporate_actions/%s/%s' % (self.endpoint, asset_manager_id, corporate_action_id)
        response = requests.delete(url)
        if response.ok:
            print("DO SOMETHING?")
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def search(self, asset_manager_ids=None, corporate_action_ids=None):
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if corporate_action_ids:
            search_params['asset_ids'] = corporate_action_ids
        url = self.endpoint + '/corporate_actions'
        response = requests.get(url, params=search_params)
        if response.ok:
            json_corp_actions = [json_to_corporate_action(json_corp_action) for json_corp_action in response.json()]
            return json_corp_actions
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def corporate_actions_by_asset_manager(self, asset_manager_id):
        url = '%s/corporate_actions/%s' % (self.endpoint, asset_manager_id)
        response = requests.get(url)
        if response.ok:
            json_corp_actions = [json_to_corporate_action(json_corp_action) for json_corp_action in response.json()]
            return json_corp_actions
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)
