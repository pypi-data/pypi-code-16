# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_exchange_url


def get_rates(from_currency, to_currency):
    # Supported currencies:
    # pm_USD, pmvoucher_USD, okpay_USD, payeer_USD, advcash_USD, btce_USD, bitcoin_BTC, litecoin_LTC, ethereum_ETH,
    # dogecoin_DOGE, monero_XMR, maidsafecoin_MAID, dash_DASH, tether_USDT, ethereumclassic_ETC, lisk_LSK, bytecoin_BCN,
    # peercoin_PPC, clams_CLAM, namecoin_NMC

    currency_map = {'BTC': 'bitcoin_BTC',
                    'ETH': 'ethereum_ETH',
                    'LTC': 'litecoin_LTC',
                    'DOGE': 'dogecoin_DOGE',
                    'XMR': 'monero_XMR',
                    'DASH': 'dash_DASH',
                    'BCN': 'bytecoin_BCN',
                    'PPC': 'peercoin_PPC',
                    'NMC': 'namecoin_NMC'}
    try:
        with urlopen(get_exchange_url('changer').format(
                from_currency=currency_map.get(from_currency.upper()),
                to_currency=currency_map.get(to_currency.upper())),
                timeout=60) as f:
            response = json.loads(f.read().decode('utf-8'))
            return response.get('rate')
    except HTTPError as error:
        print("Error: {error} {reason}.".format(error=error.code, reason=error.reason))
        return None
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
