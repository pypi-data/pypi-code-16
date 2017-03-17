#!/usr/bin/env python
'''
Provide a JSON serialized graph object, containing all or part
of the full graph available in the backend.

JSON responses are given in the format:
'''

import logging

from isoprene_pumpjack.utils import SmartResource
from isoprene_pumpjack.helpers.services import execute_cypher_get_d3

logger = logging.getLogger(__name__)

def is_node_fully_loaded(central_node_id):
    '''
    Checks if a neo Identity node is fully loaded, i.e.
    Has been directly queried from the Elastic store
    NOT as a passing reference
    '''
    logger.debug("Checking if {0} is fully loaded".format(central_node_id))
    cypher = """MATCH (s:{node_label})
                WHERE s.id = '{id}'
                RETURN s""".format(**{
                    "id": central_node_id,
                    "node_label": "Dolphin"
                })
    data = execute_cypher_get_d3(cypher, ["s"], [])
    try:
        is_fully_loaded = data["nodes"][0]["props"]["isopump_fully_loaded"]
    except (IndexError, KeyError) as e:
        is_fully_loaded = False
    logger.debug("{0} {1} fully loaded".format(central_node_id, "is" if is_fully_loaded else "is not"))
    return is_fully_loaded

def get_full_graph():
    '''Transparently pass all database data'''
    logger.debug("Getting all neo graph data")
    cypher = """MATCH (d)-[r]-()
                RETURN d, r"""
    data = execute_cypher_get_d3(cypher, ["d"], ["r"])
    return data

def get_sub_graph(central_node_id):
    '''Get subgraph - first neighbours of the selected node'''
    logger.debug("Getting neo subgraph around {0}".format(central_node_id))
    cypher = """MATCH (s:{node_label})-[r*0..1]-(d:{doc_label})-[q*0..1]-(t:{node_label})
                WHERE s.id = '{id}'
                RETURN s, r, d, q, t""".format(**{
                    "id": central_node_id,
                    "node_label": "Dolphin",
                    "doc_label": "Document"
                })
    data = execute_cypher_get_d3(cypher, ["s", "t", "d"], ["r", "q"])
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
