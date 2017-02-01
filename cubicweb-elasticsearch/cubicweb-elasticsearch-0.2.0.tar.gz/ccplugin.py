# -*- coding: utf-8 -*-
"""cubicweb-ctl plugin providing the index-in-es command

:organization: Logilab
:copyright: 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import print_function

import os.path as osp

from elasticsearch.helpers import parallel_bulk

from cubicweb.cwctl import CWCTL
from cubicweb.utils import admincnx
from cubicweb.toolsutils import Command

from cubes.elasticsearch.es import indexable_types, fulltext_indexable_rql


__docformat__ = "restructuredtext en"

HERE = osp.dirname(osp.abspath(__file__))


class IndexInES(Command):

    """Index content in ElasticSearch.

    <instance id>
      identifier of the instance

    """
    name = 'index-in-es'
    min_args = max_args = 1
    arguments = '<instance id>'
    options = [('dry-run', {'type': 'yn', 'default': False,
                            'help': 'set to True if you want to skip the insertion in ES'}),
               ('debug', {'type': 'yn', 'default': False,
                          'help': 'set to True if you want to print'
                                  'out debug info and progress'}),
               ('etypes', {'type': 'csv', 'default': '',
                           'help': 'only index given etypes '
                                   '[default:all indexable types]'}),
               ('index-name', {'type': 'string', 'default': '',
                               'help': 'override index-name if you want to use a different ID'
                                       '[default: uses index-name from all-in-one.conf]'}),
               ('except-etypes', {'type': 'string', 'default': '',
                                  'help': 'all indexable types except given etypes'
                                          '[default: []]'}),
               ]

    def run(self, args):
        """run the command with its specific arguments"""
        appid = args.pop(0)
        with admincnx(appid) as cnx:
            schema = cnx.vreg.schema
            indexer = cnx.vreg['es'].select('indexer', cnx)
            es = indexer.get_connection()
            indexer.create_index()
            if self.config.index_name:
                indexer.create_index(index_name=self.config.index_name)
            if es:
                if self.config.etypes:
                    etypes = self.config.etypes
                else:
                    etypes = indexable_types(schema,
                                             custom_skip_list=self.config.except_etypes)
                    assert self.config.except_etypes not in etypes
                if self.config.debug and not self.config.etypes:
                    print(u'found indexable_types {}'.format(
                        ','.join(etypes)))
                for _ in parallel_bulk(es,
                                       self.bulk_actions(etypes,
                                                         cnx,
                                                         index_name=self.config.index_name,
                                                         dry_run=self.config.dry_run),
                                       raise_on_error=False,
                                       raise_on_exception=False):
                            pass
            else:
                if self.config.debug:
                    print(u'no elasticsearch configuration found, skipping')

    def bulk_actions(self, etypes, cnx,
                     index_name=None, dry_run=False):
        for etype in etypes:
            rql = fulltext_indexable_rql(etype, cnx.vreg.schema)
            rset = cnx.execute(rql)
            if self.config.debug:
                print(u'indexing {} {}'.format(etype, len(rset)))
                print(u'RQL : {}'.format(rql))
            for entity in rset.entities():
                serializer = entity.cw_adapt_to('IFullTextIndexSerializable')
                json = serializer.serialize()
                if not dry_run:
                    data = {'_op_type': 'index',
                            '_index': index_name or cnx.vreg.config['index-name'],
                            '_type': etype,
                            '_id': entity.eid,
                            '_source': json
                            }
                    self.customize_data(data)
                    yield data

    def customize_data(self, data):
        pass


CWCTL.register(IndexInES)
