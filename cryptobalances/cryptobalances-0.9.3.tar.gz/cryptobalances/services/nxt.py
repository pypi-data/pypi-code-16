# -*- coding: utf-8 -*-
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from cryptobalances.config import get_api_url


def pull_request(currency, identifier):
    try:
        for i in get_peers(currency):
            url = "http://{}:7876/nxt?requestType=getBalance&account={}".format(i, identifier)
            try:
                with urlopen(url, timeout=5) as f:
                    return str(converter(int(json.loads(f.read().decode('utf-8'))['balanceNQT'])))
            except HTTPError as error:
                # If we can't connect to peer, trying to connect one more time to another peer.
                print(error)
                continue
            except URLError as error:
                print(error)
                continue
    except (ValueError, KeyError) as error:
        return error


def get_peers(currency):
    try:
        # Getting list of available peers from: http://nxtpeers.com/api/peers.php
        # Further we can to get balance connecting to peer on port 7876.
        # For example: http://{ip or domain of peer}:7876/nxt?requestType=getBalance&account=NXT-7LB8-8ZPX-3YR9-3L85B
        with urlopen(get_api_url(currency), timeout=60) as f:
            peers = list()
            response = json.loads(f.read().decode('utf-8'))
            for i in response:
                peers.append(i['screenname'])
            return peers
    except HTTPError as error:
        return error.reason
    except URLError as error:
        return error.reason
    except (ValueError, KeyError) as error:
        return error


def converter(balance):
    return round(balance/100000000.0, 5)
