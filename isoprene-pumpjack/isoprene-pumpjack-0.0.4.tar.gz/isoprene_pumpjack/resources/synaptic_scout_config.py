#!/usr/bin/env python
'''
Provide the JSON object to configure synaptic-scout with the
isoprene_pumpjack backend
'''

from isoprene_pumpjack.utils import SmartResource


config = {
    'endpoints': [
        {
            'name': 'subgraphs',
            'on': 'clickNode',
            'url': '/subgraphs',
        }
    ],
    'types': [
        {
            'type': '_default',
            'typeLabel': 'Dolphin',
            'id': 'id',
            'label': 'label',
            'color': '#42cef4'
        }
    ]
}


class SynapticScoutConfig(SmartResource):
    '''API endpoint to provide config JSON for synaptic-scout'''

    def get(self):
        '''Get JSON config for synaptic-scout'''
        self.logger.debug('Getting config')
        return config, 200

