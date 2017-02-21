import requests
import json
import time
from cryptox.public.common.common import endpoints

def order_book(self, depth):
    '''
    returns current bid/ask information for
    a given currency and exchange. 
    max allowable depth set to 100
    '''

    #set max depth to 100
    depth = 100 if depth > 100 else depth

    if self.exchange == 'poloniex':
        payload = {'currencyPair':self.currency_pair.replace('-','_'), 'depth': depth}
        resp = requests.get(endpoints['poloniex']['order_book'], params=payload)
        j_resp = resp.json()
        return {
            'asks':[ {'price':m[0], 'volume':m[1]} for m in j_resp['asks'] ], 
            'bids':[ {'price':m[0], 'volume':m[1]} for m in j_resp['bids'] ], 
            'timestamp':int(time.time())
        }

    if self.exchange == 'ccex':
        payload = {'market':self.currency_pair, 'type':'both', 'depth': depth}
        resp = requests.get(endpoints['ccex']['order_book'], params=payload)
        j_resp = resp.json()
        return {
            'asks':[ {'price':m['Rate'], 'volume':m['Quantity']} for m in j_resp['result']['sell'] ], 
            'bids':[ {'price':m['Rate'], 'volume':m['Quantity']} for m in j_resp['result']['buy'] ], 
            'timestamp':int(time.time())
        }

    return 'Exchange not found'