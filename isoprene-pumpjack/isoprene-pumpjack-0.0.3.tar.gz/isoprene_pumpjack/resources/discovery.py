#!/usr/bin/env python
'''
Provide a JSON serialized list of endpoints
'''

from isoprene_pumpjack.utils import SmartResource

discovery = {
  "kind": "discovery#restDescription",
  "discoveryVersion": "v1",
  "id": 'isoprene-pumpjack:v1',
  "name": 'isoprene-pumpjack',
  "version": 'v1',
  "revision": '1',
  "title": 'Isoprene Pumpjack',
  "description": 'Backend for synaptic-scout; request data from Neo4j, perform searches in Elastic, and pump data between the two.',
  "documentationLink": "https://isoprene-pumpjack.readthedocs.io/",
}


class Discovery(SmartResource):
    '''API endpoint to provide config JSON for synaptic-scout'''

    def get(self):
        '''Get JSON representing endpoints'''
        self.logger.debug('Getting discovery')
        return discovery, 200
