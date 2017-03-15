#!/usr/bin/env python
"""
Environment specific constants for the app
"""

import os
import re
import logging

from neo4j.v1 import GraphDatabase, basic_auth
from elasticsearch_dsl.connections import connections

logger = logging.getLogger(__name__)

# Neo
ISOPRENE_PUMPJACK_BOLT_URL = os.getenv('GRAPHENEDB_BOLT_URL', 'bolt://localhost:7687')
ISOPRENE_PUMPJACK_BOLT_USER = os.getenv('GRAPHENEDB_BOLT_USER', 'isoprenepumpjack')
ISOPRENE_PUMPJACK_BOLT_PASSWORD = os.getenv('GRAPHENEDB_BOLT_PASSWORD', 'isoprenepumpjack')

logger.info('Seting up Bolt driver')
bolt_driver = GraphDatabase.driver(
    ISOPRENE_PUMPJACK_BOLT_URL,
    auth=basic_auth(
        ISOPRENE_PUMPJACK_BOLT_USER,
        ISOPRENE_PUMPJACK_BOLT_PASSWORD
    )
)

# Elastic
ISOPRENE_PUMPJACK_ELASTICSEARCH_URL = os.getenv('BONSAI_URL', 'http://localhost:9200/')

logger.info('Seting up Elasticsearch connection')
# Determine if we need to set up using Bonsai (Heroku)
if os.getenv('BONSAI_URL'):
    logger.info('Using Bonsai hosted elasticsearch')
    # Parse the auth and host from env:
    bonsai = os.environ['BONSAI_URL']
    auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
    host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')

    # Connect to cluster over SSL using auth for best security:
    es_hosts = [{
    'host': host,
    'port': 443,
    'use_ssl': True,
    'http_auth': (auth[0],auth[1])
    }]
else:
    logger.info('Using bare elasticsearch')
    es_hosts = [ISOPRENE_PUMPJACK_ELASTICSEARCH_URL]


# Set default global connection in elasticsearch-dsl library
connections.create_connection(hosts=es_hosts, timeout=50)

