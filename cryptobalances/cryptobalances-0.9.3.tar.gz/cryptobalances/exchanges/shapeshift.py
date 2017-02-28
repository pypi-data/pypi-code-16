# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_exchange_url


def get_rates(currency_pair):
    try:
        with urlopen(get_exchange_url('shapeshift').format(currency_pair=currency_pair), timeout=60) as f:
            response = json.loads(f.read().decode('utf-8'))
            if response.get('error'):
                return None
            else:
                return response.get('rate')
    except HTTPError as error:
        return error
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
