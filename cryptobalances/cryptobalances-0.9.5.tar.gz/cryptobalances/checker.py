# -*- coding: utf-8 -*-
from cryptobalances.validator import autodetect_currency
from cryptobalances.config import default_user_agent
from cryptobalances.services import chain_request
from cryptobalances.services import eth_request
from cryptobalances.services import doge_request
from cryptobalances.services import xcp_request
from cryptobalances.services import crypto_request
from cryptobalances.services import xem_request
from cryptobalances.services import xrp_request
from cryptobalances.services import oa_request
from cryptobalances.services import omni_request
from cryptobalances.services import zcash_request
from cryptobalances.services import nxt_request
from cryptobalances.services import steem_request
from cryptobalances.services import golos_request
from cryptobalances.exchanges import poloniex_rates
from cryptobalances.exchanges import shapeshift_rates
from cryptobalances.exchanges import changer_rates
from cryptobalances.exchanges import coinomat_rates


def get_request(currency):
    try:
        supported_currencies = {'BTC': chain_request, 'LTC': chain_request,
                                'ETH': eth_request, 'DOGE': doge_request,
                                'XCP': xcp_request, 'DASH': crypto_request,
                                'PPC': crypto_request, 'CPC': crypto_request,
                                'GRT': crypto_request, 'BLK': crypto_request,
                                'XEM': xem_request, 'XRP': xrp_request,
                                'OA': oa_request, 'OMNI': omni_request,
                                'ZEC': zcash_request, 'NXT': nxt_request,
                                'STEEM': steem_request, 'GOLOS': golos_request
                                }
        return supported_currencies[currency]
    except KeyError as error:
        print("Error: {}. Reason: Currency isn't supported.".format(error))
        return None


def get_balance(currency, identifier, useragent=default_user_agent()):

    auto_currency = autodetect_currency(identifier)

    if not isinstance(auto_currency, list):
        currency = auto_currency

    return get_request(currency)(currency, identifier, useragent)


# Maybe need to add instant=True parameter for getting rates from instant exchanges such as: shapeshift, changelly
# instant=False to getting rates from exchanges: poloniex and other
def get_exchange():
    return [poloniex_rates, shapeshift_rates, changer_rates]
    # return [poloniex_rates, shapeshift_rates, changer_rates, coinomat_rates]


def get_rate(from_currency, to_currency, useragent=default_user_agent()):
    for i in get_exchange():
        rate = i(from_currency, to_currency, useragent)
        if rate:
            return rate
    return None
