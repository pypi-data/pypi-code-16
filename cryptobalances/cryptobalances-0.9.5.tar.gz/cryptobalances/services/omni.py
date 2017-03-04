# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url


def pull_request(currency, identifier, useragent):
    property_id = {'OMNI': '1'}

    try:
        request = Request(get_api_url(currency).format(property_id=property_id['OMNI'], identifier=identifier), method='GET')
        request.add_header('User-Agent', useragent)

        with urlopen(request, timeout=60) as f:
            return f.read().decode('utf-8')
    except HTTPError as error:
        return error.reason
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
