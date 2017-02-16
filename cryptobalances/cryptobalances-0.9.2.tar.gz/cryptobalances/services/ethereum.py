# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url


def pull_request(currency, identifier):

    # TODO: We need to perform validation wallet because api returns always positive response.
    # TODO: For example: http://api.etherscan.io/api?module=account&action=balance&address=bla-bla-bla&tag=latest
    # TODO: returns {"status":"1","message":"OK","result":"0"}, but it's not mean that balance is zero.
    # TODO: This is case when address of wallet not valid

    try:
        with urlopen(get_api_url(currency).format(identifier=identifier), timeout=60) as f:
            response = json.loads(f.read().decode('utf-8'))
            if response['message'] == 'NOTOK':
                # TODO: We need return more informative message if api returns error. It's not good: "NOTOK. Error!"
                return "{}. {}".format(response['message'], response['result'])
            return str(converter(int(response['result'])))
    except HTTPError as error:
        return error.reason
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error


def converter(balance):
    return round(balance/1000000000000000000.0, 5)
