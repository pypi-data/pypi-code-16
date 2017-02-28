import re
from base58 import b58decode_check


def autodetect_currency(identifier):
    try:
        if re.match('^(0x)?[0-9a-fA-F]{40}$', identifier):
            return 'ETH'
        elif re.match('^L[a-km-zA-HJ-NP-Z1-9]{33}$', identifier):
            return 'LTC'
        elif re.match('^D[a-km-zA-HJ-NP-Z1-9]{33}$', identifier):
            return 'DOGE'
        elif re.match('^X[a-km-zA-HJ-NP-Z1-9]{33}$', identifier):
            return 'DASH'
        elif re.match('^P[a-km-zA-HJ-NP-Z1-9]{33}$', identifier):
            # PeerCoin
            return 'PPC'
        elif re.match('^C[a-km-zA-HJ-NP-Z1-9]{33}$', identifier):
            # CapriCoin
            return 'CPC'
        elif re.match('^G[a-km-zA-HJ-NP-Z1-9]{33}$', identifier):
            # GrantCoin
            return 'GRT'
        elif re.match('^B[a-km-zA-HJ-NP-Z1-9]{33}$', identifier):
            # BlackCoin
            return 'BLK'
        elif re.match('^[nN][a-zA-Z0-9]{5}(-[a-zA-Z0-9]{4,6}){6}$', identifier):
            # Nem Coin
            return 'XEM'
        elif re.match('^r[1-9A-HJ-NP-Za-km-z]{25,33}$', identifier):
            # Ripple Coin
            return 'XRP'
        elif re.match('^t[1-9a-zA-Z]{34}$', identifier):
            # ZCash
            return 'ZEC'
        elif re.match('^(NXT|nxt)(-[a-zA-Z0-9]{4,5}){4}$', identifier):
            return 'NXT'
        elif re.match('^[a-z0-9\-]+$', identifier):
            return ['STEEM', 'GOLOS']
        elif b58decode_check(identifier)[0] == 19:
            # OpenAssets (Coinprism)
            return 'OA'
        else:
            # If we can't detect currency return the remaining variants
            return ['BTC', 'XCP', 'OMNI']
    except ValueError as error:
        # Function: 'b58decode_check' may throw an exception - ValueError: Invalid checksum
        return None
