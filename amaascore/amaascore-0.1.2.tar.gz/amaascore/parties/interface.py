import requests

from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface
from amaascore.parties.utils import json_to_party


class PartiesInterface(Interface):

    def __init__(self):
        endpoint = ENDPOINTS.get('parties')
        super(PartiesInterface, self).__init__(endpoint=endpoint)

    def new(self, party):
        url = self.endpoint + '/parties'
        response = requests.post(url, json=party.to_interface())
        if response.ok:
            party = json_to_party(response.json())
            return party
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def amend(self, party):
        url = '%s/parties/%s/%s' % (self.endpoint, party.asset_manager_id, party.party_id)
        response = requests.put(url, json=party.to_interface())
        if response.ok:
            party = json_to_party(response.json())
            return party
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve(self, asset_manager_id, party_id):
        url = '%s/parties/%s/%s' % (self.endpoint, asset_manager_id, party_id)
        response = requests.get(url)
        if response.ok:
            return json_to_party(response.json())
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def deactivate(self, asset_manager_id, party_id):
        url = '%s/parties/%s/%s' % (self.endpoint, asset_manager_id, party_id)
        response = requests.delete(url)
        if response.ok:
            print("DO SOMETHING?")
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def search(self, asset_manager_ids=None, party_ids=None):
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if party_ids:
            search_params['party_ids'] = party_ids
        url = self.endpoint + '/parties'
        response = requests.get(url, params=search_params)
        if response.ok:
            parties = [json_to_party(json_party) for json_party in response.json()]
            return parties
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def parties_by_asset_manager(self, asset_manager_id):
        url = '%s/parties/%s' % (self.endpoint, asset_manager_id)
        response = requests.get(url)
        if response.ok:
            parties = [json_to_party(json_party) for json_party in response.json()]
            return parties
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)
