import requests

from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface
from amaascore.market_data.utils import json_to_eod_price, json_to_fx_rate


class MarketDataInterface(Interface):

    def __init__(self):
        endpoint = ENDPOINTS.get('market_data')
        super(MarketDataInterface, self).__init__(endpoint=endpoint)

    def persist_eod_prices(self, asset_manager_id, business_date, eod_prices, update_existing_prices=True):
        """

        :param asset_manager_id:
        :param business_date: The business date for which these are rates.  Not really needed, could be derived...
        :param eod_prices:
        :param update_existing_prices:
        :return:
        """
        url = '%s/eod_prices/%s/%s' % (self.endpoint, asset_manager_id, business_date.isoformat())
        params = {'update_existing_prices': update_existing_prices}
        eod_prices_json = [eod_price.to_interface() for eod_price in eod_prices]
        response = requests.post(url, params=params, json=eod_prices_json)
        if response.ok:
            eod_prices = [json_to_eod_price(eod_price) for eod_price in response.json()]
            return eod_prices
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve_eod_prices(self, asset_manager_id, business_date):
        url = '%s/eod_prices/%s/%s' % (self.endpoint, asset_manager_id, business_date.isoformat())
        response = requests.get(url=url)
        if response.ok:
            eod_prices = [json_to_eod_price(eod_price) for eod_price in response.json()]
            return eod_prices
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def persist_fx_rates(self, asset_manager_id, business_date, fx_rates, update_existing_rates=True):
        """

        :param asset_manager_id:
        :param business_date: The business date for which these are rates.  Not really needed, could be derived...
        :param fx_rates:
        :param update_existing_rates:
        :return:
        """
        url = '%s/fx_rates/%s/%s' % (self.endpoint, asset_manager_id, business_date.isoformat())
        params = {'update_existing_rates': update_existing_rates}
        fx_rates_json = [fx_rate.to_interface() for fx_rate in fx_rates]
        response = requests.post(url, params=params, json=fx_rates_json)
        if response.ok:
            fx_rates = [json_to_fx_rate(fx_rate) for fx_rate in response.json()]
            return fx_rates
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)

    def retrieve_fx_rates(self, asset_manager_id, business_date):
        url = '%s/fx_rates/%s/%s' % (self.endpoint, asset_manager_id, business_date.isoformat())
        response = requests.get(url=url)
        if response.ok:
            fx_rates = [json_to_fx_rate(fx_rate) for fx_rate in response.json()]
            return fx_rates
        else:
            print("HANDLE THIS PROPERLY")
            print(response.content)
