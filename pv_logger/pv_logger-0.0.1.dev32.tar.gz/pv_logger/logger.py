"""read data from kacors485, cache them locally in sqlite
and finally sync them to remote InfluxDB server (assume local ssh tunnel)"""

import yaml
import logging
import time
import os
import datetime

from sqlite_influx import Config

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# setup config first, before we import the other stuff
config_file = 'config.yaml'
with open(config_file, 'r') as stream:
    logger.info("read config file {}".format(os.path.abspath(config_file)))
    config_yaml = yaml.load(stream)
Config.config.update(config_yaml)

if 'log_level' in Config.config:
    defined_level = Config.config['log_level']
    pre_defined_level = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
    if defined_level in pre_defined_level:
        level = logging.getLevelName(defined_level)
        logging.basicConfig(level = level)
        logging.getLogger().setLevel(level = level)
        logging.info("set new log level from config file to: {} ({})".
            format(level, defined_level))
    else:
        logging.warning("log level in config file not valid: {}".format(level))

# now import helpers, which initialize database
# based on config data
from sqlite_influx import sqlite
from pv_logger import watchdog
from pv_logger import kaco, sma_rs485, sbfspot

wdog_manager = watchdog.Manager()
# setup checks at import, because also in functions used (not only in main)
check_conf = Config.config['checks']['internet_connection']
wdog_manager.register_check('internet_connection',
    datetime.timedelta(seconds=check_conf['interval_seconds']),
    min_fails_in_row=check_conf['min_fails_in_row'],
    callback=watchdog.test_internet_connection)

check_conf = Config.config['checks']['port_found']
wdog_manager.register_check('port_found',
    datetime.timedelta(seconds=check_conf['interval_seconds']),
    min_fails_in_row=check_conf['min_fails_in_row'])

if 'check_read_data' in Config.config['checks']:
    check_conf = Config.config['checks']['check_read_data']
    wdog_manager.register_check('check_read_data',
        datetime.timedelta(seconds=check_conf['interval_seconds']),
        min_fails_in_row=check_conf['min_fails_in_row'])


def measurements_remove_empty(measurements):
    return {k: measurements[k] for k in measurements if measurements[k]}

def read_data():
    inverter_types = Config.config['inverter_type']

    # convert to list, if not yet
    if not isinstance(inverter_types, list):
        raise Exception('config.yaml "inverter_type" must be a list')

    measurements = {}
    for inverter_type in inverter_types:
        if inverter_type == 'kaco':
            data = kaco.read_all_inverter(wdog_manager)
        elif inverter_type == 'sma_rs485':
            data = sma_rs485.read_all_inverter(wdog_manager)
        elif inverter_type == 'sbfspot':
            data = sbfspot.read_all_inverter(wdog_manager)
        else:
            raise Exception('unknown "inverter_type" {} in configuration'.
                format(inverter_type))

        measurements.update(data)

    # clear measurements, where fields are empty
    measurements = measurements_remove_empty(measurements)

    return measurements

def main_loop():
    # get measurements
    measurements = read_data()

    # append more information
    uptime_now = watchdog.get_uptime()
    uptime_app = uptime_now - wdog_manager.start_time
    measurements['system'] = {
        'uptime_node': float(uptime_now.total_seconds()),
        'uptime_app': float(uptime_app.total_seconds()),
        'ram_free_kb': float(watchdog.get_freemem()),
    }

    # store measurements
    sqlite.store_dicts(measurements)

    sqlite.sync_to_influx()
    sqlite.archive(Config.config['archive_older_than_days'])

    # run watchdog manager
    wdog_manager.run()

def main():
    # run main loop
    while True:
        start = watchdog.get_uptime()

        main_loop()

        end = watchdog.get_uptime()
        logger.info("last main loop took %s seconds to run",
            end-start)

        time.sleep(Config.config['read_interval_seconds'])

if __name__ == '__main__':
    main()
