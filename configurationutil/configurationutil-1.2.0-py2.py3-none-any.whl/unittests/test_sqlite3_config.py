import json
import unittest

import os

from configurationutil.cfg_objects import sqlite3_config
from fdutil.path_tools import pop_path

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


@unittest.skip  # TODO: once written remove the skip!
class TestSqlite3Config(unittest.TestCase):

    def setUp(self):
        self.cfg_file = os.path.join(pop_path(__file__), u'test_sqlite3_config.db')

        self.cfg = sqlite3_config.Sqlite3Config(config_file=self.cfg_file,
                                                create=True)

        self.cfg.cfg = {u'test': 123, u'test2': 456, u'test3': 789}  # TODO
        self.cfg.save()

    def tearDown(self):
        try:
            os.remove(self.cfg_file)

        except OSError:
            pass

    def test_instantiation(self):
        self.assertEqual(self.cfg.cfg.get(u'test'), 123,  # TODO
                         u'JSONConfig instantiation failed')

        self.assertEqual(self.cfg.get(u'test'), 123,
                         u'JSONConfig instantiation failed')

    def test_instantiation_remove_file(self):
        with self.assertRaises(IOError):
            self.cfg_test = sqlite3_config.Sqlite3Config(config_file=u'does_not_exist!')

    def test_instantiation_default(self):
        self.cfg_file = os.path.join(pop_path(__file__), u'test_json_config_default.json')  # TODO

        self.cfg = sqlite3_config.Sqlite3Config(config_file=self.cfg_file,
                                                create=True)

        self.assertEqual(self.cfg.cfg, {},  # TODO
                         u'JSONConfig default instantiation failed')

    def test_instantiation_missing_default(self):

        default_template = sqlite3_config.Sqlite3Config.DEFAULT_TEMPLATE
        del sqlite3_config.Sqlite3Config.DEFAULT_TEMPLATE

        self.cfg_file = os.path.join(pop_path(__file__), u'test_json_config_missing_default.json')  # TODO

        with self.assertRaises(NotImplementedError):
            self.cfg = sqlite3_config.Sqlite3Config(config_file=self.cfg_file,
                                                    create=True)

        sqlite3_config.Sqlite3Config.DEFAULT_TEMPLATE = default_template

    def test_save(self):
        self.assertFalse(u'test4' in self.cfg)

        # Not using the setter as it auto saves!
        self.cfg.cfg[u'test4'] = u'it worked!'

        f = json.load(open(self.cfg_file))  # TODO
        self.assertFalse(u'test4' in f)
        self.assertTrue(u'test4' in self.cfg)

        self.cfg.save()

        f = json.load(open(self.cfg_file))  # TODO
        self.assertTrue(u'test4' in f)
        self.assertTrue(u'test4' in self.cfg)

    def test_find(self):

        filters = [(123, None), (456, None, u'OR')]

        self.assertEqual(self.cfg.find(filters), {u'test': 123, u'test2': 456},  # TODO
                         u'Find failed')

    def test_get(self):
        self.assertEqual(self.cfg[u'test3'], 789,
                         u'Get failed')

    def test_get_missing_item(self):
        with self.assertRaises(KeyError):
            _ = self.cfg[u'not_here']

    def test_set(self):
        self.assertTrue(u'test_set' not in self.cfg)

        self.cfg[u'test_set'] = u'Set some config'

        self.assertEqual(self.cfg[u'test_set'], u'Set some config',
                         u'Set failed')

    def test_del(self):
        self.cfg[u'test_del'] = u'Del some config'

        del self.cfg[u'test_del']

        self.assertFalse(u'test_del' in self.cfg)

    def test_iter(self):
        self.assertTrue(u'test2' in self.cfg)

    def test_len(self):
        self.assertTrue(len(self.cfg), 3)

if __name__ == u'__main__':
    unittest.main()
