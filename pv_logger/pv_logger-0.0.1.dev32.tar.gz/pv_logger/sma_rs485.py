import logging
import traceback
import os

from sqlite_influx import Config
from pyyasdi.objects import Plant

logger = logging.getLogger(__name__)

def read_all_inverter(wdog_manager):
    plant = None

    logger.info("read all inverters")

    measurements = {}
    try:
        if not os.path.exists('yasdi.ini'):
            raise Exception('could not find yasdi.ini')

        if not isinstance(plant, Plant):
            logger.info("initialize plant yasdi RS485 instance")
            plant = Plant(debug=1,
                max_devices=Config.config['sma_rs485_max_devices'])
        else:
            logger.info("reset plant yasdi RS485 instance")
            plant.reset()

        # if we make it till here without Exception, RS485 port was found
        wdog_manager.update_result('port_found', True)

        data = plant.data_all(parameter_channel=False, skip_on_timeout=True)

        if int(Config.config['sma_rs485_max_devices']) != len(data):
            logger.error("could only read %s of %s inverters",
                len(data), Config.config['sma_rs485_max_devices'])
        else:
            # read ALL inverter successfully
            wdog_manager.update_result('check_read_data', True)

        # stop plant
        plant.quit()

        # add inverter_ to inverter metric name
        renamed = {}
        for k in data:
            renamed['inverter_{}'.format(k)] = data[k]

        measurements.update(renamed)

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
