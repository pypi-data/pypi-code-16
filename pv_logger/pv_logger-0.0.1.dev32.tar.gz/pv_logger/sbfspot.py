import logging
import traceback
import sqlite3
from sqlalchemy import desc

from sqlite_influx import Config, sqlite

logger = logging.getLogger(__name__)

def get_rows():
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conn = sqlite3.connect(Config.config['sbfspot_sqlite_file'])
    conn.row_factory = dict_factory
    c = conn.cursor()

    # TODO number of records hard coded, therfore we can only retrieve
    # these many different inverter data
    c.execute('SELECT * FROM SpotData Order by TimeStamp desc limit 5')
    data = c.fetchall()
    
    measurements = {}
    for d in data:
        # add inverter_ to metric name of inverter
        key = 'inverter_{}'.format(d['Serial'])
        if not key in measurements:
            measurements[key] = d

    return measurements

def read_all_inverter(wdog_manager):
    logger.info("read all inverters")

    measurements = {}
    try:
        data = get_rows()
        measurements.update(data)

        # if we make it till here without Exception, sbfspot stuff was found
        wdog_manager.update_result('port_found', True)

        # set communication info
        measurements['communication'] = {
            'last_request_status': 'ok'
        }
    except Exception:
        trace = traceback.format_exc()
        logger.exception("error while requesting inverters")

        # set communication info
        measurements['communication'] = {
            'last_request_status': 'error',
            'error_msg': trace
        }

    return measurements
