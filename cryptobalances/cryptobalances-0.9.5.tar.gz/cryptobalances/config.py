# -*- coding: utf-8 -*-


def get_api_url(currency):
    api_urls = {"BTC": "https://chain.so/api/v2/get_address_balance/{network}/{identifier}",
                "LTC": "https://chain.so/api/v2/get_address_balance/{network}/{identifier}",
                "ETH": "http://api.etherscan.io/api?module=account&action=balance&address={identifier}&tag=latest",
                "DOGE": "http://dogechain.info/api/v1/address/balance/{identifier}",
                "XCP": "http://xcp.blockscan.com/api2?module=address&action=balance&btc_address={identifier}",
                "DASH": "http://chainz.cryptoid.info/dash/api.dws?q=getbalance&a={identifier}",
                "PPC": "http://chainz.cryptoid.info/ppc/api.dws?q=getbalance&a={identifier}",
                "CPC": "http://chainz.cryptoid.info/cpc/api.dws?q=getbalance&a={identifier}",
                "GRT": "http://chainz.cryptoid.info/grt/api.dws?q=getbalance&a={identifier}",
                "BLK": "http://chainz.cryptoid.info/blk/api.dws?q=getbalance&a={identifier}",
                "XEM": "http://bigalice3.nem.ninja:7890/account/get?address={identifier}",
                "XRP": "https://data.ripple.com/v2/accounts/{identifier}/balances",
                "OA": "https://api.coinprism.com/v1/addresses/{identifier}",
                "OMNI": "http://omnichest.info/requeststat.aspx?stat=balance&prop={property_id}&address={identifier}",
                "ZEC": "https://api.zcha.in/v1/mainnet/accounts/{identifier}",
                "NXT": "http://nxtpeers.com/api/peers.php",
                "STEEM": "wss://steemd.steemit.com",
                "GOLOS": "wss://ws.golos.io"}
    return api_urls[currency]


def get_exchange_url(exchange):
    api_url = {"poloniex": "https://poloniex.com/public?command=returnTicker",
               "shapeshift": "https://shapeshift.io/rate/{from_currency}_{to_currency}",
               "changer": "https://www.changer.com/api/v2/rates/{from_currency}/{to_currency}",
               "coinomat": "https://coinomat.com/api/v1/get_xrate.php?f={from_currency}&t={to_currency}"}
    return api_url[exchange]


def get_supported_currencies(data_type):
    # parameter data_type - type of return value.
    # Such as: list, tuple, dictionary

    currencies = ['BTC', 'LTC', 'ETH',
                  'DOGE', 'XCP', 'DASH',
                  'PPC', 'CPC', 'GRT',
                  'BLK', 'XEM', 'XRP',
                  'OA', 'OMNI', 'ZEC',
                  'NXT', 'STEEM', 'GOLOS']
    if data_type == 'list':
        return currencies
    elif data_type == 'tuple':
        temp_list = list()
        for i in zip(currencies, currencies):
            temp_list.append(i)
        return tuple(temp_list)
    elif data_type == 'dict':
        return dict(zip(currencies, currencies))


def default_user_agent():
    return "Mozilla/5.0 (Windows NT 6.1; WOW64) " \
           "AppleWebKit/537.36 (KHTML, like Gecko) " \
           "Chrome/55.0.2883.87 Safari/537.36"
