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

"""cubicweb-elasticsearch specific hooks and operations"""

import logging

from elasticsearch.exceptions import ConnectionError
from urllib3.exceptions import ProtocolError

from cubicweb.server import hook
from cubicweb.predicates import score_entity
from cubes.elasticsearch.es import indexable_types, fulltext_indexable_rql, CUSTOM_ATTRIBUTES

log = logging.getLogger(__name__)


def entity_indexable(entity):
    return entity.cw_etype in indexable_types(entity._cw.vreg.schema) or \
        entity.cw_etype in CUSTOM_ATTRIBUTES


class ContentUpdateIndexES(hook.Hook):
    """detect content change and updates ES indexing"""

    __regid__ = 'elasticsearch.contentupdatetoes'
    __select__ = hook.Hook.__select__ & score_entity(entity_indexable)
    events = ('after_update_entity', 'after_add_entity')
    category = 'es'

    def __call__(self):
        if self.entity.cw_etype == 'File':
            return  # FIXME hack!
        IndexEsOperation.get_instance(self._cw).add_data(self.entity)


class RelationsUpdateIndexES(hook.Hook):
    """detect relations changes and updates ES indexing"""

    __regid__ = 'elasticsearch.relationsupdatetoes'
    events = ('after_add_relation', 'before_delete_relation')
    category = 'es'

    def __call__(self):
        # XXX add a selector for object and subject
        for entity in (self._cw.entity_from_eid(self.eidfrom),
                       self._cw.entity_from_eid(self.eidto)):
            cw_etype = entity.cw_etype
            if cw_etype == 'File':
                return  # FIXME hack!
            if (cw_etype in indexable_types(entity._cw.vreg.schema) or
                    cw_etype in CUSTOM_ATTRIBUTES):
                IndexEsOperation.get_instance(self._cw).add_data(entity)


class IndexEsOperation(hook.DataOperationMixIn, hook.Operation):

    def postcommit_event(self):
        indexer = self.cnx.vreg['es'].select('indexer', self.cnx)
        es = indexer.get_connection()
        if es is None or not self.cnx.vreg.config['index-name']:
            log.error('no connection to ES (not configured) skip ES indexing')
            return
        for entity in self.get_data():
            rql = fulltext_indexable_rql(entity.cw_etype,
                                         entity._cw.vreg.schema,
                                         eid=entity.eid)
            indexable_entity = self.cnx.execute(rql).one()
            serializer = indexable_entity.cw_adapt_to('IFullTextIndexSerializable')
            json = serializer.serialize()
            try:
                # TODO option pour coté async ? thread
                kwargs = dict(index=indexer.index_name,
                              id=entity.eid,
                              doc_type=entity.cw_etype,
                              body=json)
                if json.get('parent'):
                    kwargs['parent'] = json.pop('parent')
                else:  # TODO only for types that have parents
                    kwargs['routing'] = entity.eid
                es.index(**kwargs)
            except (ConnectionError, ProtocolError):
                log.debug('Failed to index in hook, could not connect to ES')
