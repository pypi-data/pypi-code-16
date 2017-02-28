# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url


# More calls of api for zcash currency are described here:  The ZChain API - https://explorer.zcha.in/api

def pull_request(currency, identifier):
    try:
        request = Request(get_api_url(currency).format(identifier=identifier), method='GET')

        # If perform the request with user-agent the default for python api returns 403 http error
        request.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/55.0.2883.87 Safari/537.36')

        with urlopen(request, timeout=60) as f:
            return str(json.loads(f.read().decode('utf-8'))['balance'])
    except HTTPError as error:
        response = json.loads(error.read().decode('utf-8'))
        return response['error']
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
