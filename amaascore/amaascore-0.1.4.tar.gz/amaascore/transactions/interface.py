import requests

from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface
from amaascore.transactions.utils import json_to_transaction, json_to_position


class TransactionsInterface(Interface):

    def __init__(self):
        endpoint = ENDPOINTS.get('transactions')
        super(TransactionsInterface, self).__init__(endpoint=endpoint)

    def new(self, transaction):
        url = self.endpoint + '/transactions'
        response = requests.post(url, json=transaction.to_interface())
        if response.ok:
            transaction = json_to_transaction(response.json())
            return transaction
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def amend(self, transaction):
        url = '%s/transactions/%s/%s' % (self.endpoint, transaction.asset_manager_id, transaction.transaction_id)
        response = requests.put(url, json=transaction.to_interface())
        if response.ok:
            transaction = json_to_transaction(response.json())
            return transaction
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve(self, asset_manager_id, transaction_id):
        url = '%s/transactions/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        response = requests.get(url)
        if response.ok:
            return json_to_transaction(response.json())
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def transactions_by_asset_manager(self, asset_manager_id):
        url = '%s/transactions/%s' % (self.endpoint, asset_manager_id)
        response = requests.get(url)
        if response.ok:
            transactions = [json_to_transaction(json_transaction) for json_transaction in response.json()]
            return transactions
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def cancel(self, asset_manager_id, transaction_id):
        url = '%s/transactions/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        response = requests.delete(url)
        if response.ok:
            print("DO SOMETHING?")
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def search(self, asset_manager_ids=None, transaction_ids=None):
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if transaction_ids:
            search_params['transaction_ids'] = transaction_ids
        url = self.endpoint + '/transactions'
        response = requests.get(url, params=search_params)
        if response.ok:
            transactions = [json_to_transaction(json_transaction) for json_transaction in response.json()]
            return transactions
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def position_search(self, asset_manager_ids=None, asset_book_ids=None, account_ids=None, accounting_types=None,
                        asset_ids=None, position_date=None):
        url = self.endpoint + '/positions'
        search_params = {}
        # Potentially roll into a loop
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if asset_book_ids:
            search_params['asset_book_ids'] = asset_book_ids
        if account_ids:
            search_params['account_ids'] = account_ids
        if accounting_types:
            search_params['accounting_types'] = accounting_types
        if asset_ids:
            search_params['asset_ids'] = asset_ids
        if position_date:
            search_params['position_date'] = position_date
        response = requests.get(url, params=search_params)
        if response.ok:
            positions = [json_to_position(json_position) for json_position in response.json()]
            return positions
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def positions_by_asset_manager_book(self, asset_manager_id, asset_book_id):
        url = '%s/positions/%s/%s' % (self.endpoint, asset_manager_id, asset_book_id)
        response = requests.get(url)
        if response.ok:
            positions = [json_to_position(json_position) for json_position in response.json()]
            return positions
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def positions_by_asset_manager(self, asset_manager_id):
        url = '%s/positions/%s' % (self.endpoint, asset_manager_id)
        response = requests.get(url)
        if response.ok:
            positions = [json_to_position(json_position) for json_position in response.json()]
            return positions
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def allocate_transaction(self, asset_manager_id, transaction_id, allocation_type, allocation_dicts):
        """

        :param asset_manager_id:
        :param transaction_id:
        :param allocation_type:
        :param allocation_dicts:
        :return:
        """
        url = '%s/allocations/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        params = {'allocation_type': allocation_type}
        response = requests.post(url, params=params, json=allocation_dicts)
        if response.ok:
            allocations = [json_to_transaction(json_allocation) for json_allocation in response.json()]
            return allocations
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve_transaction_allocations(self, asset_manager_id, transaction_id):
        """

        :param asset_manager_id:
        :param transaction_id:
        :return:
        """
        url = '%s/allocations/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        response = requests.get(url)
        if response.ok:
            allocations = [json_to_transaction(json_allocation) for json_allocation in response.json()]
            return allocations
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def upsert_transaction_asset(self, transaction_asset_json):
        """
        This API should not be called in normal circumstances as the asset cache will populate itself from the assets
        which are created via the Assets API.  However, it can be useful for certain testing scenarios.
        :param transaction_asset_json:
        :return:
        """
        url = self.endpoint + '/assets'
        response = requests.post(url, json=transaction_asset_json)
        if response.ok:
            print("DO SOMETHING?")
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def upsert_transaction_book(self, transaction_book_json):
        """
        This API should not be called in normal circumstances as the book cache will populate itself from the book
        which are created via the Books API.  However, it can be useful for certain testing scenarios.
        :param transaction_book_json:
        :return:
        """
        url = self.endpoint + '/books'
        response = requests.post(url, json=transaction_book_json)
        if response.ok:
            print("DO SOMETHING?")
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def net_transactions(self, asset_manager_id, transaction_ids, netting_type='Net'):
        """

        :param asset_manager_id: The asset_manager_id of the netting set owner
        :param transaction_ids:  A list of transaction_ids to net
        :param netting_type:
        :return:
        """
        url = '%s/netting/%s' % (self.endpoint, asset_manager_id)
        params = {'netting_type': netting_type}
        response = requests.post(url, params=params, json=transaction_ids)
        if response.ok:
            net_transaction = json_to_transaction(response.json())
            return net_transaction
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve_netting_set(self, asset_manager_id, transaction_id):
        """
        Returns all the transaction_ids associated with a single netting set.  Pass in the ID for any transaction in
        the set.
        :param asset_manager_id:  The asset_manager_id for the netting set owner.
        :param transaction_id: A transaction_id of an entry within the netting set.
        :return:
        """
        url = '%s/netting/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        response = requests.get(url)
        if response.ok:
            net_transaction_id, netting_set_json = response.json().items()[0]
            return net_transaction_id, [json_to_transaction(net_transaction) for net_transaction in netting_set_json]
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)
