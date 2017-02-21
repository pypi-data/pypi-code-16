import requests
import json
from cryptox.public.common.common import endpoints

def get_currency_pairs(self):
    '''
    return valid currency pairs for one or  
    all exchanges with positive 24 hour volume.
    '''
    reqs = {}

    if self.exchange == 'all':
        for key, value in endpoints.items():
            reqs[key] = value['24_hour_volume']

    else:
        reqs[self.exchange] = endpoints[self.exchange]['24_hour_volume']


    currency_pairs = []

    for key, value in reqs.items():
        if key == 'poloniex':
            resp = requests.get(value)
            j_resp = resp.json()
            for pair in j_resp:
                if '_' in pair:
                    for curr in j_resp[pair]:
                        if float(j_resp[pair][curr]) > 0:
                            currency_pairs.append(pair.replace('_','-'))
                            break

        if key == 'ccex':
            resp = requests.get(value)
            j_resp = resp.json()
            for cp in j_resp['result']:
                if cp['Volume'] > 0:
                    currency_pairs.append(cp['MarketName'])

    return list(set(currency_pairs))