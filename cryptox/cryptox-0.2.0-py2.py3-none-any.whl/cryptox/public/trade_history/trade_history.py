import requests
import json
import time
from cryptox.public.common.common import endpoints

def trade_history(self, depth):
    '''
    returns trade history for a
    given currency and exchange.
    max allowable depth set to 100
    '''

    #set max depth to 100
    depth = 100 if depth > 100 else depth

    #date, type, price, volume, total
    if self.exchange == 'poloniex':
        payload = {'currencyPair':self.currency_pair.replace('-','_')}
        resp = requests.get(endpoints['poloniex']['trade_history'], params=payload)
        j_resp = resp.json()[:depth]
        result = [
            {'date':t['date'], 'price':t['rate'],'type':t['type'],'volume':t['amount'],'total':t['total']} 
            for t in j_resp 
        ]
        return {
            'history':result,
            'timestamp':int(time.time())
        }

    if self.exchange == 'ccex':
        payload = {'market':self.currency_pair, 'count': depth}
        resp = requests.get(endpoints['ccex']['trade_history'], params=payload)
        j_resp = resp.json()['result']
        result = [
            {'date':t['TimeStamp'], 'price':t['Price'],'type':t['OrderType'].lower(),'volume':t['Quantity'],'total':t['Total']} 
            for t in j_resp 
        ]
        return {
            'history':result,
            'timestamp':int(time.time())
        }

    return 'Exchange not found'