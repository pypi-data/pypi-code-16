# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url


def pull_request(currency, identifier):
    property_id = {'OMNI': '1'}

    try:
        with urlopen(get_api_url(currency).format(property_id=property_id['OMNI'], identifier=identifier), timeout=60) as f:
            return f.read().decode('utf-8')
    except HTTPError as error:
        return error.reason
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error
