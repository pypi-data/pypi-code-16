# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url


def pull_request(currency, identifier, useragent):
    # TODO: I have noticed that time to time the following api is working very slow:
    # TODO: http://xcp.blockscan.com/api2?module=address&action=balance&btc_address={identifier}
    # TODO: I think we need to find any alternative api.
    try:
        request = Request(get_api_url(currency).format(identifier=identifier), method='GET')
        request.add_header('User-Agent', useragent)

        with urlopen(request, timeout=60) as f:
            response = json.loads(f.read().decode('utf-8'))
            if response['status'] == 'error':
                return response['message']
            elif response['status'] == 'success':
                # TODO: We have the ability to return all the assets
                data = dict()
                for asset in response['data']:
                    data[asset['asset']] = asset['balance']
                return data['XCP']
    except HTTPError as error:
        return error.reason
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
