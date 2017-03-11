import unittest

from ea.es.tests.aggregate import TestAggegrate
from ea.es.tests.aggregate import TestEntity
from ea.es.tests.aggregate import TestValueObject
import ea.schema


class SchemaTestCase(unittest.TestCase):

    def setUp(self):
        self.obj = TestAggegrate()

    def test_dump_succeeds(self):
        state = self.obj.__getstate__()

    def test_load_succeeds(self):
        state = self.obj.__getstate__()
        obj = TestAggegrate()
        obj.__setstate__(state)

    def test_default_is_set(self):
        self.assertTrue(self.obj.default is not None, repr(self.obj.default))

    def test_field_has_no_default(self):
        self.assertEquals(self.obj.__schema__._declared_fields['default'].default,
            ea.schema.missing)

    def test_many_is_initialized_as_list(self):
        self.assertIsInstance(self.obj.valueobject, list)
