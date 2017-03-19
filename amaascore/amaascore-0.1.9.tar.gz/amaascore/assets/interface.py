from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from amaascore.assets.utils import json_to_asset
from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface


class AssetsInterface(Interface):

    def __init__(self, logger=None):
        endpoint = ENDPOINTS.get('assets')
        self.logger = logger or logging.getLogger(__name__)
        super(AssetsInterface, self).__init__(endpoint=endpoint)

    def new(self, asset):
        url = self.endpoint + '/assets'
        response = self.session.post(url, json=asset.to_interface())
        if response.ok:
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def amend(self, asset):
        url = '%s/assets/%s/%s' % (self.endpoint, asset.asset_manager_id, asset.asset_id)
        response = self.session.put(url, json=asset.to_interface())
        if response.ok:
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id, asset_id):
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        response = self.session.get(url)
        if response.ok:
            return json_to_asset(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def deactivate(self, asset_manager_id, asset_id):
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        json = {'asset_status': 'Inactive'}
        response = self.session.patch(url, json=json)
        if response.ok:
            return json_to_asset(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_ids=None, asset_ids=None):
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if asset_ids:
            search_params['asset_ids'] = asset_ids
        url = self.endpoint + '/assets'
        response = self.session.get(url, params=search_params)
        if response.ok:
            assets = [json_to_asset(json_asset) for json_asset in response.json()]
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def assets_by_asset_manager(self, asset_manager_id):
        url = '%s/assets/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            assets = [json_to_asset(json_asset) for json_asset in response.json()]
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()
