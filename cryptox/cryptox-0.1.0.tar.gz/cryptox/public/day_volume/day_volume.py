import requests
import json
from cryptox.public.common.common import endpoints

def day_volume(self, currency_pairs):
    '''
    return 24 hour volume for specific currency pair
    or for a list of currency pairs
    '''
    if currency_pairs == None:
        currency_pairs = [self.currency_pair]

    if self.exchange == 'poloniex':
        resp = requests.get(endpoints['poloniex']['24_hour_volume'])
        j_resp = resp.json()
        volume = {}

        for pair in currency_pairs:
            split_pair = pair.split('-')
            if pair.replace('-','_') in j_resp:
                volume[pair.replace('_','-')] = {  
                    split_pair[0]:float(j_resp[pair.replace('-','_')][split_pair[0]]),
                    split_pair[1]:float(j_resp[pair.replace('-','_')][split_pair[1]])
                }

        return volume

    if self.exchange == 'ccex':
        resp = requests.get(endpoints['ccex']['24_hour_volume'])
        j_resp = resp.json()
        volume = {}

        for pair in j_resp['result']:
            if pair['MarketName'] in currency_pairs:
                split_pair = pair['MarketName'].split('-')
                volume[pair['MarketName']] = {split_pair[0]:pair['Volume'], split_pair[1]:pair['BaseVolume']}

        return volume

    return 'Exchange not found'