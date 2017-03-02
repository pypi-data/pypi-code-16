import re
import collections
from mock import patch
from unittest import TestCase
from printen.mixins import ElasticsearchIndexMixin
from printen.exceptions import Misconfigured
import printen.config
import printen.mixins
import printen.utils


ELASTICSEARCH_SETTINGS = {
    'ELASTICSEARCH_DELETE_OLD_INDICES': True,
    'ELASTICSEARCH_INDEX_NAME': 'test',
    'ELASTICSEARCH_TYPE_CLASSES': [],
    'ELASTICSEARCH_CONNECTION_PARAMS': {
        'hosts': 'http://127.0.0.1:9200',
    },
}


class DummyIndex(ElasticsearchIndexMixin):
    pass


class UtilsTests(TestCase):
    def setUp(self):
        printen.config.configure(ELASTICSEARCH_SETTINGS)

    def tearDown(self):
        # Ensure we have a clean settings object
        # between runs
        printen.config._search_types = None
        printen.config.settings = printen.config.SettingsObject()
        printen.utils._elasticsearch_indices = collections.defaultdict(
            lambda: []
        )

    def test_get_indices(self):
        # This will raise a misconfigured when nothing
        # is configured for type classes yet.

        with self.assertRaises(Misconfigured):
            printen.utils.get_indices()

        printen.config.configure({
            'ELASTICSEARCH_TYPE_CLASSES': [
                'some.missing.class'
            ]
        })

        # And it will still raise if they're wrong
        with self.assertRaises(Misconfigured):
            printen.utils.get_indices()

        printen.config.configure({
            'ELASTICSEARCH_TYPE_CLASSES': [
                '{}.DummyIndex'.format(__name__)
            ]
        })

        self.assertEqual(printen.utils.get_indices(), {
            'index': [DummyIndex]
        })

    @patch('printen.utils.es.get_aliases', autospec=True)
    def test_get_indices_from_aliases(self, mock_get_aliases):
        get_aliases_return = {
            'test-123455': {
                'aliases': {
                    'test': {}
                }
            }
        }
        mock_get_aliases.return_value = get_aliases_return

        self.assertEqual(
            printen.utils.get_indices_from_aliases(search_aliases=['test']),
            ['test-123455']
        )

    def test_get_alias_names(self):
        self.assertEqual(
            printen.utils.get_alias_names([('test', 'test-123455')]),
            ['test']
        )

        self.assertEqual(
            printen.utils.get_alias_names([]),
            []
        )

        self.assertEqual(
            printen.utils.get_alias_names([
                ('test', 'test-123456'),
                ('test', 'test-234567')
            ]),
            ['test']
        )

        self.assertEqual(
            printen.utils.get_alias_names([
                ('test', 'test-123456'),
                ('tests', 'test-234567')
            ]),
            ['test', 'tests']
        )

    @patch('printen.utils.es.get_aliases', autospec=True)
    @patch('printen.utils.es.update_aliases', autospec=True)
    def test_create_aliases(self, mock_update_aliases, mock_get_aliases):
        get_aliases_return = {
            'test-123456': {
                'aliases': {
                    'test': {}
                }
            }
        }
        actions = {
            'actions': [
                {
                    'remove': {
                        'index': 'test-123456',
                        'alias': 'test'
                    }
                },
                {
                    'add': {
                        'index': 'test-234567',
                        'alias': 'test'
                    }
                }
            ]
        }

        mock_get_aliases.return_value = get_aliases_return
        printen.utils.create_aliases([('test', 'test-234567')])
        mock_update_aliases.assert_called_with(actions)

    def test_find_search_types(self):
        # A fairly meh test, but meh.
        self.assertItemsEqual(
            printen.utils.find_search_types(printen),
            [
                printen.mixins.PeeweeElasticsearchIndexMixin,
                printen.mixins.DjangoElasticsearchIndexMixin
            ]
        )

    @patch('printen.utils.es.delete_indices', autospec=True)
    def test_delete_indices(self, mocked):
        printen.utils.delete_indices(['foo', ])
        mocked.assert_called_with(['foo', ])

    @patch('printen.utils.es.create_index', autospec=True)
    @patch('printen.utils.es.get_aliases', autospec=True)
    @patch('printen.utils.es.update_aliases', autospec=True)
    def test_create_indices(self, mocked_update, mocked_get, mocked_create):
        printen.config.configure({
            'ELASTICSEARCH_TYPE_CLASSES': [
                '{}.DummyIndex'.format(__name__)
            ]
        })

        printen.utils.create_indices()
        assert(mocked_create.called)
        assert(mocked_create.call_args[0][1] == {})
        assert(re.match(
            'index-[0-9]{8}-[0-9]{6}',
            mocked_create.call_args[0][0]
        ))
