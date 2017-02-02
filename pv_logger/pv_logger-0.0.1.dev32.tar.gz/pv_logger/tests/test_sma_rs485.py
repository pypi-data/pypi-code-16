import unittest as unittest
try:
    from unittest import mock
except ImportError:
    import mock

from pv_logger import logger as pvlogger

pvlogger.Config.config['inverter_type'] = ['sma_rs485']

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
        pvlogger.main_loop()

        rows = self.get_rows()
        self.remove_all_rows()

        self.assertEqual(rows[0]['fields']['last_request_status'], 'error')
        self.assertEqual(len(rows), 2)

        sma_rs485_loaded = ('sma_rs485.py' in repr(rows[0]['fields']))
        self.assertEqual(sma_rs485_loaded, True)

    @mock.patch('pv_logger.sma_rs485.read_all_inverter')
    def test_write(self, read_mock):
        # mock answer, check if it can be written to influxdb
        mock_data = {
            'WR6K-006 SN:2000141813': {
                'T-Start-Fan': 70.0,
                'Upv-Start': 300.0,
            },
            'WR42MS04 SN:1100067554': {
                'Iac': 0,
                'Pac': 0,
                'Firmware-BFR': 0,
                'Netz-Ein': 0,
            }
        }
        read_mock.return_value = mock_data

        self.remove_all_rows()
        pvlogger.main_loop()
        rows = self.get_rows()

        print("rows are", rows)
        self.assertEqual(len(rows), 3)

        # check that it passed to influxdb
        influx = pvlogger.sqlite.influx.client.query("SELECT * FROM /WR42*/ ORDER BY time DESC LIMIT 1")
        influx_item = None
        for f in influx:
            influx_item = f[0]

        print("influx item", influx_item)
        print("WARNING: this test needs a influxdb backend to pass!!")
        self.assertEqual(influx_item['Firmware-BFR'], 0)
