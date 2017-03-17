#!/usr/bin/env python
'''
Central execution points for non-python services
'''

import logging

from neo4j.v1 import GraphDatabase, basic_auth

from isoprene_pumpjack.constants.environment import environment
from isoprene_pumpjack.utils.neo_to_d3 import neo_to_d3
from isoprene_pumpjack.exceptions import GraphServiceException, DocumentServiceException

logger = logging.getLogger(__name__)

# TODO - some error handling here?
def execute_cypher(cypher_statement):
    logger.debug("Executing cypher statement")
    bolt_driver = GraphDatabase.driver(
        environment["ISOPRENE_PUMPJACK_BOLT_URL"],
        auth=basic_auth(
            environment["ISOPRENE_PUMPJACK_BOLT_USER"],
            environment["ISOPRENE_PUMPJACK_BOLT_PASSWORD"]
        )
    )
    with bolt_driver.session() as session:
        result = session.run(cypher_statement)
    return result

def execute_cypher_get_d3(cypher_statement, nodeLabels=[], linkLabels=[]):
    logger.debug("Executing cypher and returning as d3 dict")
    result = execute_cypher(cypher_statement)
    data = neo_to_d3(result, nodeLabels, linkLabels)
    return data
