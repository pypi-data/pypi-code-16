import baskt
import unittest

host = 'http://127.0.0.1:5000'

class TestBasktMethods(unittest.TestCase):

    def test_create_baskt(self):
        key = baskt.create(host=host)
        self.assertNotEqual(len(key), 0)

    def test_open_baskt(self):
        key = baskt.create(host=host)
        db = baskt.open(key, host=host)
        self.assertNotEqual(db, None)

    def test_set_baskt_key(self):
        key = baskt.create(host=host)
        db = baskt.open(key, host=host)
        db.set('key', 'value')
        self.assertEqual(db.get('key'), 'value')

    def test_rem_baskt_key(self):
        key = baskt.create(host=host)
        db = baskt.open(key, host=host)
        db.set('key', 'value')
        db.rem('key')
        self.assertEqual(db.get('key'), None)

    def test_get_baskt_key_default(self):
        key = baskt.create(host=host)
        db = baskt.open(key, host=host)
        self.assertEqual(db.get('key', 'default'), 'default')

if __name__ == '__main__':
    unittest.main()
