# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_exchange_url


def get_rates(from_currency, to_currency, useragent):
    try:
        # BTC - Bitcoin, LTC - Litecoin, BTCD - BitcoinDark, PPC - Peercoin, NXT - NXT(NeXT), PERFECT - Perfect Money USD,
        # EGOPAY - Ego Pay USD, OKPAY - OK Pay USD, VISAMASTER - withdrawal to Visa / Mastercard,
        # WMV - Webmoney VND(Vietnam), VTC - VTC Pay VND(Vietnam), COINO - CoinoUSD NXT asset,
        # BTCE - BTC'e USD code

        # This service has problem with ssl cert:
        # ssl.SSLError(1,'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:600)')
        # Temporary disabled this api.
        request = Request(get_exchange_url('coinomat').format(
                          from_currency=from_currency,
                          to_currency=to_currency), method='GET')
        request.add_header('User-Agent', useragent)

        with urlopen(request, timeout=60) as f:
            response = json.loads(f.read().decode('utf-8'))
            if response.get('error'):
                return None
            else:
                return response.get('xrate')
    except HTTPError as error:
        return error
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
