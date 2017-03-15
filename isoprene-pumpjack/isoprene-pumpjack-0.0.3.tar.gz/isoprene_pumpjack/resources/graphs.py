#!/usr/bin/env python
'''
Provide a JSON serialized graph object, containing all or part
of the full graph available in the backend.

JSON responses are given in the format:
'''

from isoprene_pumpjack.constants.environment import bolt_driver
from isoprene_pumpjack.utils import SmartResource
import isoprene_pumpjack.utils.neo_to_d3 as neo_to_d3


def get_full_graph():
    '''Transparently pass all database data'''
    with bolt_driver.session() as session:
        result = session.run("""MATCH (d)-[r]-()
                        RETURN d, r""")
    
    data = neo_to_d3.neo_to_d3(result, ["d"], ["r"])
    return data

def get_sub_graph(central_node_id):
    '''Get subgraph - first neighbours of the selected node'''
    with bolt_driver.session() as session:
        result = session.run("""MATCH (s:{node_label})-[r*0..1]-(d:{doc_label})-[q*0..1]-(t:{node_label})
                        WHERE s.id = '{id}'
                        RETURN s, r, d, q, t""".format(**{
                            "id": central_node_id,
                            "node_label": "Dolphin",
                            "doc_label": "Document"
                        }))
    
    data = neo_to_d3.neo_to_d3(result, ["s", "t", "d"], ["r", "q"])
    return data


class SubGraph(SmartResource):
    '''API endpoint to provide config JSON for synaptic-scout'''

    def get(self, central_node_id):
        '''Get JSON representing subgraph centered on a single node'''
        self.logger.debug('Getting sub graph for {0}'.format(central_node_id))
        sub_graph = get_sub_graph(central_node_id)
        return sub_graph, 200


class FullGraph(SmartResource):
    '''Provide all graph data from backend'''

    def get(self):
        '''Get JSON representing full graph'''
        self.logger.debug('Getting full graph')
        full_graph = get_full_graph()
        return full_graph, 200
