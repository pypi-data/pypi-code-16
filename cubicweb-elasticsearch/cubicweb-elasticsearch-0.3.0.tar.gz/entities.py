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

"""cubicweb-elasticsearch entity's classes"""

import collections

from cubicweb import view, neg_role
from cubicweb.predicates import is_instance

from cubicweb.appobject import AppObject

from cubes.elasticsearch import es


def deep_update(d1, d2):
    for key, value in d2.iteritems():
        if isinstance(value, collections.Mapping):
            d1[key] = deep_update(d1.get(key, {}), value)
        else:
            d1[key] = d2[key]
    return d1


class EsRegistry(AppObject):
    __registry__ = 'es'


class Indexer(EsRegistry):
    __regid__ = 'indexer'
    settings = {
        'settings': {
            'analysis': {
                'analyzer': {
                    'default': {'filter': ['standard',
                                           'my_ascii_folding',
                                           'lowercase',
                                           'french_snowball'],
                                'tokenizer': 'standard'}
                },
                'filter': {'my_ascii_folding': {'preserve_original': True,
                                                'type': 'asciifolding'},
                           'french_snowball': {'type': 'snowball',
                                               'language': 'French'}}
            },
        }
    }

    @property
    def index_name(self):
        return self._cw.vreg.config['index-name']

    def get_connection(self):
        self.create_index()
        return es.get_connection(self._cw.vreg.config)

    def create_index(self, index_name=None, custom_settings=None):
        index_name = index_name or self.index_name
        if custom_settings is None:
            settings = self.settings
        else:
            settings = {}
            deep_update(settings, self.settings)
            deep_update(settings, custom_settings)
        es_cnx = es.get_connection(self._cw.vreg.config)
        if es_cnx is not None:
            es.create_index(es_cnx, index_name, settings)


class IFullTextIndexSerializable(view.EntityAdapter):
    """Adapter to serialize an entity to a bare python structure that may be
    directly serialized to e.g. JSON.
    """

    __regid__ = 'IFullTextIndexSerializable'
    __select__ = is_instance('Any')

    def serialize(self, complete=False):
        entity = self.entity
        if complete:
            entity.complete()
        data = {
            'cw_etype': entity.cw_etype,
            'eid': entity.eid,
            'cwuri': entity.cwuri,
        }
        data.update(entity.cw_attr_cache)
        self.update_parent_info(data, entity)
        # TODO take a look at what's in entity.cw_relation_cache
        return data

    def update_parent_info(self, data, entity):
        """this is where a client cube would feed the 'parent' index

            data['parent'] = entity.entry_of[0]
        """
        pass


class File(IFullTextIndexSerializable):
    __select__ = IFullTextIndexSerializable.__select__ & is_instance('File')

    def serialize(self, complete=False):
        """this could be a generic implementation of fulltext_containers indexation, but for

        now we can not return more than one parent json which is fine
        for Files
        """
        for rschema, role in self._cw.vreg.schema['File'].fulltext_containers():
            for parent in self.entity.related(
                    rschema.type, role=neg_role(role)).entities():
                return parent.cw_adapt_to(
                    'IFullTextIndexSerializable').serialize(complete)
        return {}
