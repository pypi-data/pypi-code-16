# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url


def pull_request(currency, identifier, useragent):
    try:
        request = Request(get_api_url(currency).format(identifier=identifier.replace('-', '')), method='GET')
        request.add_header('User-Agent', useragent)

        with urlopen(request, timeout=60) as f:
            response = json.loads(f.read().decode('utf-8'))
            if 'error' in response:
                return 'Error: {}. Reason: {}'.format(response['error'], response['message'])
            return str(converter(response['account']['balance']))
    except HTTPError as error:
        return error.reason
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error


def converter(balance):
    return round(balance/1000000.0, 5)
