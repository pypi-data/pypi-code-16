# -*- coding: utf-8 -*-
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging

from elasticsearch.exceptions import ConnectionError
from urllib3.exceptions import ProtocolError
from elasticsearch_dsl.connections import connections

from rql.utils import rqlvar_maker

INDEXABLE_TYPES = None

# customization mechanism, in your cube, add your type as a key, and a list of
# additionnal attributes
# eg. CUSTOM_ATTRIBUTES['BlogEntry'] = ('description',)
CUSTOM_ATTRIBUTES = {}

log = logging.getLogger(__name__)


def indexable_types(schema, custom_skip_list=None):
    '''
    introspect indexable types
    '''
    global INDEXABLE_TYPES
    if INDEXABLE_TYPES is not None:
        return INDEXABLE_TYPES
    indexable_types = []
    skip_list = ['TrInfo', 'EmailAddress']
    if custom_skip_list:
        skip_list = skip_list + custom_skip_list
    for eschema in schema.entities():
        if eschema.type in skip_list:
            continue
        if not eschema.final:
            # check eschema.fulltext_relations() ? (skip wf_info_for ?
            # )
            if list(eschema.indexable_attributes()):
                indexable_types.append(eschema.type)
    INDEXABLE_TYPES = indexable_types
    return indexable_types


def fulltext_indexable_rql(etype, schema, eid=None):
    '''
    Generate RQL with fulltext_indexable attributes for a given entity type

    :eid:
       defaults to None, set it to an eid to get RQL for a single element (used in hooks)
    '''
    varmaker = rqlvar_maker()
    V = next(varmaker)
    rql = ['WHERE %s is %s' % (V, etype)]
    if eid:
        rql.append('%s eid %i' % (V, eid))
    var = next(varmaker)
    selected = []
    for rschema in schema.eschema(etype).indexable_attributes():
        attr = rschema.type
        var = next(varmaker)
        rql.append('%s %s %s' % (V, attr, var))
        selected.append(var)
    for rschema, tschema in schema.eschema(etype).attribute_definitions():
        if rschema.type == 'eid':
            continue
        if tschema.type in ('Int', 'Float'):
            attr = rschema.type
            var = next(varmaker)
            rql.append('%s %s %s' % (V, attr, var))
            selected.append(var)
    for attr in ('creation_date', 'modification_date', 'cwuri') + CUSTOM_ATTRIBUTES.get(etype, ()):
        var = next(varmaker)
        rql.append('%s %s %s' % (V, attr, var))
        selected.append(var)
    # TODO inlined relations ?
    return 'Any %s,%s %s' % (V, ','.join(selected),
                             ','.join(rql))


def create_index(es, index_name, settings=None):
    """Create ``index_name`` if it doesn't already exist in ES


    Parameters
    ----------

    :es:
      the elastic search connection

    :index_name:
      the index name

    :settings:
      mapping and analyzer definitions

    """
    try:
        if index_name and not es.indices.exists(index=index_name):
            es.indices.create(index=index_name,
                              body=settings)
    except (ConnectionError, ProtocolError):
        log.debug('Failed to index in hook, could not connect to ES')


def get_connection(config):
    '''
    Get connection with config object, creates a persistent connexion and
    '''
    try:
        return connections.get_connection()
    except KeyError:
        locations = config['elasticsearch-locations']
        if locations:
            # TODO sanitize locations
            es = connections.create_connection(hosts=locations.split(','),
                                               timeout=20)
            return es
        # TODO else ? raise KeyError - return None is OK?
