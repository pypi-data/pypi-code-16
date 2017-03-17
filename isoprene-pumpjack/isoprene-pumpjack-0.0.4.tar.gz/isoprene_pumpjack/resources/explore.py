#!/usr/bin/env python
'''
Provide smart responses to requests, only reaching back into Elastic
when Neo does not contain the data required.
'''

from isoprene_pumpjack.resources.graphs import get_sub_graph, is_node_fully_loaded
from isoprene_pumpjack.resources.search import seed_neo_graph
from isoprene_pumpjack.utils import SmartResource

def get_smart_subgraph(central_node_id):
    fully_loaded = is_node_fully_loaded(central_node_id)
    if not fully_loaded:
        seed_neo_graph(central_node_id)
    subgraph = get_sub_graph(central_node_id)
    return subgraph


class SmartSubGraph(SmartResource):
    '''If a subgraph exists already in Neo. return it.
    
    Otherwise, load the data from Elastic, then return it.'''

    def get(self, central_node_id):
        '''Get JSON representing subgraph centered on a single node'''
        self.logger.debug('Smartly getting sub graph for {0}'.format(central_node_id))

        sub_graph = get_smart_subgraph(central_node_id)
        return sub_graph, 200
