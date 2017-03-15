#!/usr/bin/env python
'''
Provide a JSON serialized set of search results.
'''

import logging
import json

from flask import request
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, Index, DocType, Text, Nested, InnerObjectWrapper

from isoprene_pumpjack.utils import SmartResource
from isoprene_pumpjack.utils.neo_to_d3 import neo_to_d3
from isoprene_pumpjack.constants.environment import bolt_driver

logger = logging.getLogger(__name__)

i = Index('dolphins')

@i.doc_type
class Dolphin(DocType):
    id = Text()
    label = Text()

@i.doc_type
class DolphinSighting(DocType):
    dolphins = Text()


def dolphin_label_hits(label):
    '''Search for all records of a dolphin by label'''
    q = Q('match', dolphins=label)
    s = Search().query(q).index('dolphins').doc_type(DolphinSighting)
    logger.debug('Executing elastic search {0}'.format(s.to_dict()))
    response = s.execute()
    logger.debug('Search found {0} results'.format(response.hits.total))
    return response.hits.hits

def merge_hits_to_node(hits):
    '''Collate document records to nodes and links, and upload to neo'''
    logger.debug('Merging {0} elastic documents to neo node'.format(len(hits)))

    # Create central node, the main focus of the search query
    with bolt_driver.session() as session:
        # For each document returned by the query, store extraneous data
        for document in hits:
            document_id = document["_id"]
            dolphins = document["_source"]["dolphins"]
            
            for dolphin in dolphins:
                session.run("""MERGE (s:{doc_label} {{ id: '{doc_id}', label: '{doc_id}' }})
                            ON CREATE SET s.isopump_load_initial = timestamp()
                            ON MATCH SET s.isopump_load_last = timestamp()
                            MERGE (d:{neo_label} {{ id: '{peripheral_id}', label: '{peripheral_id}' }})
                            ON CREATE SET d.isopump_load_initial = timestamp()
                            ON MATCH SET d.isopump_load_last = timestamp()
                            MERGE (d)-[:{source_label}]->(s)
                            """.format(**{
                                "knows_label": "Knows",
                                "neo_label": "Dolphin",
                                "doc_id": document_id,
                                "doc_label": "Document",
                                "source_label": "Source",
                                "peripheral_id": dolphin
                            }))
                logger.debug('New dolphin and document nodes created')


class SearchDolphins(SmartResource):
    '''API endpoint to provide config JSON for synaptic-scout'''

    def get(self):
        '''Get documents containinga single dolphin by id and label'''
        self.logger.debug('Searching dolphins')
        query_id = request.args.get('id', '')
        query_label = request.args.get('label', '')

        results = dolphin_label_hits(query_label)
        return results, 200


class SeedGraph(SmartResource):
    '''Seed a node from elastic to neo and return the node id'''

    def get(self):
        '''Get documents containing a single dolphin by id and label'''
        self.logger.debug('Seeding graph')
        query_label = request.args.get('label', '')

        hits = dolphin_label_hits(query_label)
        merge_hits_to_node(hits)

        return {"id": query_label}, 201

