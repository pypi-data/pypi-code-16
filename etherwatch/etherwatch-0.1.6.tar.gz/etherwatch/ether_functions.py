# /usr/bin/env python

# Standard library
import datetime

# Third party
from coinbase.wallet.client import Client as CoinbaseClient

# project
from etherwatch.api_keys import COINBASE_KEYS
from etherwatch.positions import POSITIONS


class EtherFunctions:

    @staticmethod
    def get_coinbase_client():
        client = CoinbaseClient(
            COINBASE_KEYS['api_key'],
            COINBASE_KEYS['api_secret']
        )
        return client

    @staticmethod
    def price_correct(price):
        return (price + (price * 0.0149))

    @staticmethod
    def get_positions(eth_price, person):
        co_position = (eth_price - EtherFunctions.price_correct(
            person['price']
        ))
        gross_position = co_position * person['quantity']
        return gross_position

    # Coinbase
    @staticmethod
    def get_eth_exchange(curr_string='USD'):
        client = EtherFunctions.get_coinbase_client()
        #print(client.get_buy_price())
        eth_exchange_rates = client.get_exchange_rates(currency='ETH')['rates']
        eth_to_usd = eth_exchange_rates['USD']
        return float(eth_to_usd)

    @staticmethod
    def get_eth_exchange_usd():
        return EtherFunctions.get_eth_exchange()

    @staticmethod
    def get_eth_exchange_btc():
        return EtherFunctions.get_eth_exchange('BTC')

    @staticmethod
    def set_sign(position):
        if position >= 0:
            sign = "+"
        else:
            sign = "-"
        return sign
