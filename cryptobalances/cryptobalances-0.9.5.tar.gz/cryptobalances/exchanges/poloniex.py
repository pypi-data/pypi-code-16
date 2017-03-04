# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_exchange_url


def get_rates(from_currency, to_currency, useragent):
    try:
        # currencies have been swapped because poloniex returns incorrect value.
        # For example: BTC_ETH returns value 0.0143859. But it's rate ETH to BTC
        request = Request(get_exchange_url('poloniex'), method='GET')
        request.add_header('User-Agent', useragent)

        currency_pair = '{to_currency}_{from_currency}'.format(from_currency=from_currency, to_currency=to_currency)
        with urlopen(request, timeout=60) as f:
            pair = json.loads(f.read().decode('utf-8')).get(currency_pair)
            if pair:
                return pair.get('last')
            return None
    except HTTPError as error:
        return error
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
