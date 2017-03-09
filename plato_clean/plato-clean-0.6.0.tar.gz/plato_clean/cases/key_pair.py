from plato_clean.cases import get_resource
from plato_clean.cases import post_resource


class CleanKeyPairs():

    def run(self, API, sleep):
        key_pairs = get_resource(API, 'DescribeKeyPairs', {
            'status': ['active']
        }, 'keyPairSet')

        # delete key_pairs
        key_pair_ids = [kp['keyPairId'] for kp in key_pairs]
        post_resource(API, 'DeleteKeyPairs', key_pair_ids, 'keyPairIds')
