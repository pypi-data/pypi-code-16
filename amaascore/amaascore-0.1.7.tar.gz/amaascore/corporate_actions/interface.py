from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface
from amaascore.corporate_actions.utils import json_to_corporate_action


class CorporateActionsInterface(Interface):

    def __init__(self, logger=None):
        endpoint = ENDPOINTS.get('corporate_actions')
        self.logger = logger or logging.getLogger(__name__)
        super(CorporateActionsInterface, self).__init__(endpoint=endpoint)

    def new(self, corporate_action):
        url = self.endpoint + '/corporate_actions'
        response = self.session.post(url, json=corporate_action.to_interface())
        if response.ok:
            corporate_action = json_to_corporate_action(response.json())
            return corporate_action
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def amend(self, corporate_action):
        url = '%s/corporate_actions/%s/%s' % (self.endpoint, corporate_action.asset_manager_id,
                                              corporate_action.corporate_action_id)
        response = self.session.put(url, json=corporate_action.to_interface())
        if response.ok:
            corporate_action = json_to_corporate_action(response.json())
            return corporate_action
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id, corporate_action_id):
        url = '%s/corporate_actions/%s/%s' % (self.endpoint, asset_manager_id, corporate_action_id)
        response = self.session.get(url)
        if response.ok:
            return json_to_corporate_action(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def cancel(self, asset_manager_id, corporate_action_id):
        url = '%s/corporate_actions/%s/%s' % (self.endpoint, asset_manager_id, corporate_action_id)
        json = {'corporate_action_status': 'Cancelled'}
        response = self.session.patch(url, json=json)
        if response.ok:
            return json_to_corporate_action(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_ids=None, corporate_action_ids=None):
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if corporate_action_ids:
            search_params['asset_ids'] = corporate_action_ids
        url = self.endpoint + '/corporate_actions'
        response = self.session.get(url, params=search_params)
        if response.ok:
            json_corp_actions = [json_to_corporate_action(json_corp_action) for json_corp_action in response.json()]
            return json_corp_actions
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def corporate_actions_by_asset_manager(self, asset_manager_id):
        url = '%s/corporate_actions/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            json_corp_actions = [json_to_corporate_action(json_corp_action) for json_corp_action in response.json()]
            return json_corp_actions
        else:
            self.logger.error(response.text)
            response.raise_for_status()
