import unittest as unittest
import os
try:
    from unittest import mock
except ImportError:
    import mock

from pv_logger import logger as pvlogger

pvlogger.Config.config['inverter_type'] = ['sbfspot']

dir_path = os.path.dirname(os.path.realpath(__file__))
pvlogger.Config.config['sbfspot_sqlite_file'] =  os.path.join(dir_path, 'test_sbfspot.db')

class HighlevelTest(unittest.TestCase):
    def get_rows(self):
        rows = pvlogger.sqlite.session.query(pvlogger.sqlite.History).all()
        rows_converted = [pvlogger.sqlite.history_to_dict(row) for row in rows]
        for item in rows_converted:
            print("row in db", item)

        return rows_converted

    def remove_all_rows(self):
        pvlogger.sqlite.session.query(pvlogger.sqlite.History).delete()

    def test_loop(self):
        self.remove_all_rows()
        pvlogger.main_loop()
        rows = self.get_rows()
        self.remove_all_rows()

        print("rows are", rows)
        self.assertEqual(len(rows), 3)
