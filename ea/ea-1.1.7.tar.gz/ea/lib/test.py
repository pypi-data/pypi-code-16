import copy
import unittest

from ea.lib.datastructures import DTO


class SchemaTestCase(unittest.TestCase):
    schema_class = None

    def setUp(self):
        self.schema = self.schema_class()

    def load(self, *args, **kwargs):
        return self.schema.load(*args, **kwargs)

    def get_params(self, override=None, exclude=None, only=None):
        obj = copy.deepcopy(self.valid_params)
        obj.update(override or {})
        only = set(only or obj.keys())
        keys = (only & set(obj.keys())) ^ set(exclude or set())
        return DTO({x: obj.get(x) for x in keys})

    def assert_attr_required(self, attname):
        params, errors = self.load(
            self.get_params(exclude=[attname]))
        self.assertIn(attname, errors)
        self.assertEqual(len(errors), 1, repr(errors))

    def assertAttributeRequired(self, attname):
        return self.assert_attr_required(attname)

    def assertAttributeNotRequired(self, attname):
        params, errors = self.load(
            self.get_params(exclude=[attname]))
        self.assertTrue(not errors, repr(errors))

    def assertDefaultsTo(self, attname, value):
        params, errors = self.load(
            self.get_params(exclude=[attname]))
        self.assertEqual(params[attname], value)

    def assert_attr_notnull(self, attname):
        params, errors = self.load(
            self.get_params(override={attname: None}))
        self.assertIn(attname, errors)
        self.assertEqual(len(errors), 1, repr(errors))
