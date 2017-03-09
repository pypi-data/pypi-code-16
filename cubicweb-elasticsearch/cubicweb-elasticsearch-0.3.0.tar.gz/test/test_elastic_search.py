from __future__ import print_function

import sys
import unittest
from io import StringIO
from itertools import repeat

from mock import patch

from elasticsearch_dsl.faceted_search import FacetedResponse

from cubicweb.devtools import testlib
from cubicweb.cwconfig import CubicWebConfiguration
from cubes.elasticsearch import ccplugin
from cubes.elasticsearch.es import (indexable_types,
                                    fulltext_indexable_rql)


# TODO - find a way to configure ElasticSearch as non threaded while running tests
# so that the traces show the full stack, not just starting from connection.http_*
class ExportElasticSearchTC(testlib.AutoPopulateTest):
    # ignore ComputedRelations
    ignored_relations = set(
        ('narrower_concept', 'hidden_label', 'preferred_label', 'alternative_label', ))

    def setup_database(self):
        super(ExportElasticSearchTC, self).setup_database()
        self.orig_config_for = CubicWebConfiguration.config_for
        config_for = lambda appid: self.config  # noqa
        CubicWebConfiguration.config_for = staticmethod(config_for)
        self.config['elasticsearch-locations'] = 'http://nonexistant.elastic.search:9200'
        self.config['index-name'] = 'unittest_index_name'

    def to_test_etypes(self):
        with self.admin_access.repo_cnx() as cnx:
            types = indexable_types(cnx.repo)
        return types

    def tearDown(self):
        CubicWebConfiguration.config_for = self.orig_config_for
        super(ExportElasticSearchTC, self).tearDown()

    def test_indexable_types(self):
        with self.admin_access.repo_cnx() as cnx:
            self.assertNotEquals(
                len(indexable_types(cnx.vreg.schema)), 0)

    @patch('elasticsearch.client.Elasticsearch.index', unsafe=True)
    @patch('elasticsearch.client.Elasticsearch.bulk', unsafe=True)
    @patch('elasticsearch.client.indices.IndicesClient.exists', unsafe=True)
    @patch('elasticsearch.client.indices.IndicesClient.create', unsafe=True)
    def test_ccplugin(self, create, exists, bulk, index):
        # TODO disable hook!!! then remove index mock
        with self.admin_access.repo_cnx() as cnx:
            cnx.disable_hook_categories('es')
            with cnx.allow_all_hooks_but('es'):
                self.auto_populate(10)
        bulk.reset_mock()
        cmd = [self.appid, '--dry-run', 'yes']
        sys.stdout = out = StringIO()
        try:
            ccplugin.IndexInES(None).main_run(cmd)
        finally:
            sys.stdout = sys.__stdout__
        self.assertEquals('', out.getvalue())
        create.assert_not_called()
        bulk.assert_not_called()

        cmd = [self.appid, '--dry-run', 'yes', '--debug', 'yes']
        sys.stdout = out = StringIO()
        try:
            ccplugin.IndexInES(None).main_run(cmd)
        finally:
            sys.stdout = sys.__stdout__
        self.assert_('found ' in out.getvalue())
        create.assert_not_called()
        bulk.assert_not_called()

        # TODO try wrong option
        # cmd = [self.appid, '--wrong-option', 'yes']

        cmd = [self.appid]
        sys.stdout = StringIO()
        try:
            ccplugin.IndexInES(None).main_run(cmd)
        finally:
            sys.stdout = sys.__stdout__
        with self.admin_access.repo_cnx() as cnx:
            self.assert_(cnx.execute('Any X WHERE X is %(etype)s' %
                                     {'etype': indexable_types(cnx.vreg.schema)[0]}))
        # TODO - put this somewhere where it tests on the first get_connection
        # create.assert_called_with(ignore=400,
        #                          index='unittest_index_name',
        #                          body=INDEX_SETTINGS)
        bulk.assert_called()
        # TODO ? check called data

    @patch('elasticsearch.client.indices.IndicesClient.create', unsafe=True)
    @patch('elasticsearch.client.indices.IndicesClient.exists', unsafe=True)
    @patch('elasticsearch.client.Elasticsearch.index', unsafe=True)
    def test_es_hooks_create(self, index, exists, create):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity('BlogEntry', title=u'Article about stuff',
                              content=u'content herer')
            cnx.commit()
            index.assert_called()

    @patch('elasticsearch.client.indices.IndicesClient.create', unsafe=True)
    @patch('elasticsearch.client.indices.IndicesClient.exists', unsafe=True)
    @patch('elasticsearch.client.Elasticsearch.index', unsafe=True)
    def test_es_hooks_modify(self, index, exists, create):
        with self.admin_access.cnx() as cnx:
            entity = cnx.create_entity('BlogEntry', title=u'Article about stuff',
                                       content=u'content herer')
            cnx.commit()
            index.reset_mock()
            entity.cw_set(title=u'Different title')
            cnx.commit()
            index.assert_called()


def mock_execute_150(*args, **kwargs):
    return mock_execute(100)


def mock_execute_15(*args, **kwargs):
    return mock_execute(15)


def mock_execute_1(*args, **kwargs):
    return mock_execute(1)


def mock_execute(nb_results):
    result = {'_source': {'description': 'test',
                          'cwuri': 'http://example.org/123',
                          'eid': 123,
                          'title': 'test'},
              '_type': 'BaseContent',
              '_score': 1}
    search = {'hits': {'hits': repeat(result, nb_results),
                       'total': nb_results
                       }}
    return FacetedResponse(search, search)


def mock_cnx(*args, **kwargs):
    return True


class ElasticSearchViewsTC(testlib.CubicWebTC):

    # TODO generate X tests ranging the number of results from 1 to 150
    @patch('elasticsearch_dsl.search.Search.execute', new=mock_execute_1)
    @patch('elasticsearch_dsl.connections.connections.get_connection', new=mock_cnx)
    def test_search_view_1(self):
        with self.new_access('anon').web_request() as req:
            # self._cw.form.get('search'))
            self.view('esearch', req=req, template=None)

    @patch('elasticsearch_dsl.search.Search.execute', new=mock_execute_15)
    @patch('elasticsearch_dsl.connections.connections.get_connection', new=mock_cnx)
    def test_search_view_15(self):
        with self.new_access('anon').web_request() as req:
            # self._cw.form.get('search'))
            self.view('esearch', req=req, template=None)

    @patch('elasticsearch_dsl.search.Search.execute', new=mock_execute_150)
    @patch('elasticsearch_dsl.connections.connections.get_connection', new=mock_cnx)
    def skip_test_search_view_150(self):
        with self.new_access('anon').web_request() as req:
            # self._cw.form.get('search'))
            self.view('esearch', req=req, template=None)


class ElasticsearchTC(testlib.CubicWebTC):

    def test_1(self):
        with self.admin_access.cnx() as cnx:
            schema = cnx.vreg.schema
            etype = 'Person'
            rql = fulltext_indexable_rql(etype, schema)
            self.assertIn('age', rql)
            self.assertNotIn('eid', rql)
            self.assertEqual(rql.count('modification_date'), 1)


if __name__ == '__main__':
    unittest.main()
