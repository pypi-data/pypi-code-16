import unittest
import httplib

from elasticsearch_dsl.connections import connections

from cubicweb.predicates import is_instance

from cubes.elasticsearch.es import CUSTOM_ATTRIBUTES
from cubes.elasticsearch.entities import IFullTextIndexSerializable


CUSTOM_ATTRIBUTES['Blog'] = ('title',)


class BlogFTIAdapter(IFullTextIndexSerializable):
    __select__ = (IFullTextIndexSerializable.__select__ &
                  is_instance('BlogEntry'))

    def update_parent_info(self, data, entity):
        data['parent'] = entity.entry_of[0].eid


class RealESTestMixin(object):

    @classmethod
    def setUpClass(cls):
        try:
            httplib.HTTPConnection('localhost:9200').request('GET', '/')
        except:
            raise unittest.SkipTest('No ElasticSearch on localhost, skipping test')
        super(RealESTestMixin, cls).setUpClass()

    def setup_database(self):
        super(RealESTestMixin, self).setup_database()
        self.config.global_set_option('elasticsearch-locations',
                                      'http://localhost:9200')
        self.config.global_set_option('index-name',
                                      'unittest_index_name')

    def tearDown(self):
        try:
            with self.admin_access.cnx() as cnx:
                indexer = cnx.vreg['es'].select('indexer', cnx)
                es = indexer.get_connection()
                es.indices.delete(self.config['index-name'])
        finally:
            # remove default connection if there's one
            try:
                connections.remove_connection('default')
            except KeyError:
                pass
            super(RealESTestMixin, self).tearDown()
