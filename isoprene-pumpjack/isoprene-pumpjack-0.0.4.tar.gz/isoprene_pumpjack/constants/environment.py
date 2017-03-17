#!/usr/bin/env python
"""
Environment specific constants for the app
"""

import os
import re
import logging
import pprint

from elasticsearch_dsl.connections import connections


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream = logging.StreamHandler()
stream.setFormatter(logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s'))
stream.setLevel(logging.DEBUG)
logger.addHandler(stream)

def environment_sweep(environment_variable_names_list=[], default_value=None):
    '''
    Check a list of environment variables (in order) for any value.

    If no value found, fall back to the default value.
    '''
    logger.debug("Sweeping environment variables")
    for env_var_name in environment_variable_names_list:
        env_var_value = os.getenv(env_var_name, None)
        logger.debug("Checking {0}, value {1}".format(env_var_name, env_var_value))
        if env_var_value:
            return env_var_value
    logger.debug("Falling back to default {0}".format(default_value))
    return default_value


def get_environement():
    '''
    Grab config from the environment. Allows for logging and live environment changes
    '''
    logger.debug("Getting environment config")
    config = {}
    # Neo

    config["ISOPRENE_PUMPJACK_BOLT_URL"] = environment_sweep(
            [
                'ISOPRENE_PUMPJACK_BOLT_URL',
                'GRAPHENEDB_BOLT_URL'
            ],
            'bolt://localhost:7687'
    )
    config["ISOPRENE_PUMPJACK_BOLT_USER"] = environment_sweep(
            [
                'ISOPRENE_PUMPJACK_BOLT_USER',
                'GRAPHENEDB_BOLT_USER'
            ],
            'isoprenepumpjack'
    )
    config["ISOPRENE_PUMPJACK_BOLT_PASSWORD"] = environment_sweep(
            [
                'ISOPRENE_PUMPJACK_BOLT_PASSWORD',
                'GRAPHENEDB_BOLT_PASSWORD'
            ],
            'isoprenepumpjack'
    )

    # Elastic
    config["ISOPRENE_PUMPJACK_ELASTICSEARCH_URL"] = environment_sweep(
            [
                'ISOPRENE_PUMPJACK_ELASTICSEARCH_URL',
                'BONSAI_URL'
            ],
            'http://localhost:9200/'
    )

    logger.debug('Seting up Elasticsearch connection')
    # Determine if we need to set up using Bonsai (Heroku)
    if os.getenv('BONSAI_URL'):
        logger.debug('Using Bonsai hosted elasticsearch')
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
        logger.debug('Using bare elasticsearch')
        es_hosts = [config["ISOPRENE_PUMPJACK_ELASTICSEARCH_URL"]]


    # Set default global connection in elasticsearch-dsl library
    connections.create_connection(hosts=es_hosts, timeout=50)
    logger.info("Configuration loaded:\n{0}".format(pprint.pformat(config)))
    return config

environment = get_environement()
