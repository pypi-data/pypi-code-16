# -*- coding: utf-8 -*-
from steemapi import SteemNodeRPC
from cryptobalances.config import get_api_url


def pull_request(currency, identifier):
    try:
        client = SteemNodeRPC(get_api_url(currency))
        return client.get_account(identifier).get('balance').split(' ')[0]
    # Need to know which exceptions might throwing here
    except (ValueError, KeyError) as error:
        return error
