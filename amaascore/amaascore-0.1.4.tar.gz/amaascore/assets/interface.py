import requests

from amaascore.assets.utils import json_to_asset
from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface


class AssetsInterface(Interface):

    def __init__(self):
        endpoint = ENDPOINTS.get('assets')
        super(AssetsInterface, self).__init__(endpoint=endpoint)

    def new(self, asset):
        url = self.endpoint + '/assets'
        response = requests.post(url, json=asset.to_interface())
        if response.ok:
            asset = json_to_asset(response.json())
            return asset
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def amend(self, asset):
        url = '%s/assets/%s/%s' % (self.endpoint, asset.asset_manager_id, asset.asset_id)
        response = requests.put(url, json=asset.to_interface())
        if response.ok:
            asset = json_to_asset(response.json())
            return asset
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve(self, asset_manager_id, asset_id):
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        response = requests.get(url)
        if response.ok:
            return json_to_asset(response.json())
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def deactivate(self, asset_manager_id, asset_id):
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        response = requests.delete(url)
        if response.ok:
            print("DO SOMETHING?")
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def search(self, asset_manager_ids=None, asset_ids=None):
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if asset_ids:
            search_params['asset_ids'] = asset_ids
        url = self.endpoint + '/assets'
        response = requests.get(url, params=search_params)
        if response.ok:
            assets = [json_to_asset(json_asset) for json_asset in response.json()]
            return assets
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def assets_by_asset_manager(self, asset_manager_id):
        url = '%s/assets/%s' % (self.endpoint, asset_manager_id)
        response = requests.get(url)
        if response.ok:
            assets = [json_to_asset(json_asset) for json_asset in response.json()]
            return assets
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)
