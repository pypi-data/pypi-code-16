# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url

# Ripple has a good api for getting different information. Api method reference: https://ripple.com/build/data-api-v2/
# This URL is working but not stable: https://api.ripple.com/v1/accounts/{identifier}/balances?


def pull_request(currency, identifier):
    try:
        with urlopen(get_api_url(currency).format(identifier=identifier), timeout=60) as f:
            response = json.loads(f.read().decode('utf-8'))
            for i in response['balances']:
                if i['currency'] == 'XRP':
                    return i['value']
    except HTTPError as error:
        response = json.loads(error.read().decode('utf-8'))
        return 'Error: {}. Reason: {}'.format(error.reason, response['message'])
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
