#!/usr/bin/env python
'''
Provide a JSON serialized graph object, containing all or part
of the full graph available in the backend.

JSON responses are given in the format:
'''

import logging

from elasticsearch import Elasticsearch, TransportError
from elasticsearch_dsl import Search, Q, Index

from isoprene_pumpjack.helpers.services import execute_cypher
from isoprene_pumpjack.utils import SmartResource
from isoprene_pumpjack.utils.dolphins import dolphins
from isoprene_pumpjack.resources.search import Dolphin, DolphinSighting

logger = logging.getLogger(__name__)

def reset_graph():
    execute_cypher("MATCH (n) DETACH DELETE n")


def set_graph(data):
    for node in data["nodes"]:
        execute_cypher(
            """CREATE (a:Dolphin {{ id: '{id}', label: '{label}' }})""".format(
                **node
            ))

    for link in data["links"]:
        execute_cypher(
            """MATCH (s:Dolphin {{ id: '{source}' }}), (t:Dolphin {{ id: '{target}' }})
            CREATE (s)-[:knows]->(t)""".format(
                **link
        ))


class ResetDolphins(SmartResource):
    '''Debug endpoint - set neo4j as dolphins graph'''

    def get(self):
        '''Drop database and upload dolphins JSON data into Neo4j'''
        self.logger.debug('Resetting neo4j to dolphins')
        reset_graph()
        set_graph(dolphins)
        return {}, 201

class NeoReset(SmartResource):
    '''Debug endpoint - reset neo4j'''

    def get(self):
        '''Drop database'''
        self.logger.debug('Resetting neo4j')
        reset_graph()
        return {}, 204


def reset_elastic():
    '''Drop dolphins elastic index'''
    i = Index('dolphins')
    try:
        i.delete()
        logger.debug('Dolphins index was dropped')
    except TransportError as e:
        if e.status_code == 404:
            logger.info('Dolphins index was not dropped as it was not found')
        else:
            raise
    

def create_dolphins_index():
    i = Index('dolphins')

    # create the index, including DocType mappings
    i.create()

    for link in dolphins["links"]:
        # instantiate the document
        sighting_doc = DolphinSighting()
        # assign some field values, can be values or lists of values
        sighting_doc.dolphins = [
            list((x['label'] for x in dolphins['nodes']
                        if x["id"] == link["source"]))[0],
            list((x["label"] for x in dolphins['nodes']
                        if x["id"] == link["target"]))[0]
        ]

        # save the document into the cluster
        sighting_doc.save()


class ElasticReset(SmartResource):
    '''Debug endpoint - reset elastic'''

    def get(self):
        '''Drop database'''
        self.logger.debug('Resetting elastic')
        reset_elastic()
        return {}, 204


class IndexDolphins(SmartResource):
    '''Debug endpoint - create an Elastic dolphins index'''

    def get(self):
        '''Create and load dolphins index'''
        self.logger.debug('Indexing dolphins in elastic')
        reset_elastic()
        response = create_dolphins_index()
        return {}, 201


