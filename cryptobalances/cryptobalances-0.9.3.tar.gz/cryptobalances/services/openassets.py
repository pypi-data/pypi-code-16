# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url


def pull_request(currency, identifier):
    try:
        with urlopen(get_api_url(currency).format(identifier=identifier), timeout=60) as f:
            response = json.loads(f.read().decode('utf-8'))
            return str(response['balance'])
    except HTTPError as error:
        response = json.loads(error.read().decode('utf-8'))
        return 'Error: {}. Reason: {}'.format(error.reason, response['ErrorCode'])
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
