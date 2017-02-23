import requests

from amaascore.asset_managers.utils import json_to_asset_manager
from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface


class AssetManagersInterface(Interface):
    """
    The interface to the Asset Managers service for reading Asset Manager information.
    """

    def __init__(self):
        endpoint = ENDPOINTS.get('asset_managers')
        super(AssetManagersInterface, self).__init__(endpoint=endpoint)

    def new(self, asset_manager):
        url = '%s/asset_managers' % self.endpoint
        response = requests.post(url, json=asset_manager.to_interface())
        if response.ok:
            return json_to_asset_manager(response.json())
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve(self, asset_manager_id):
        url = '%s/asset_managers/%s' % (self.endpoint, asset_manager_id)
        response = requests.get(url)
        if response.ok:
            return json_to_asset_manager(response.json())
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def deactivate(self, asset_manager_id):
        """
        Is is only possible to deactivate an asset manager if your client_id is also the client_id that was used
        to originally create the asset manager.

        :param asset_manager_id:
        :return:
        """
        url = '%s/asset_managers/%s' % (self.endpoint, asset_manager_id)
        response = requests.delete(url)
        if response.ok:
            print("DO SOMETHING?")
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def search(self, asset_manager_ids=None, client_ids=None):
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if client_ids:
            search_params['client_ids'] = client_ids
        url = self.endpoint + '/asset_managers'
        response = requests.get(url, params=search_params)
        if response.ok:
            assets = [json_to_asset_manager(json_asset_manager) for json_asset_manager in response.json()]
            return assets
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)


