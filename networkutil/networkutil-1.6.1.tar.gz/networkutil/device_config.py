
import logging_helper
from _metadata import __version__, __authorshort__, __module_name__
from resources import templates, schema
from configurationutil import Configuration, cfg_params
from networkutil.endpoint_config import Endpoints

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
DEVICE_CONFIG = u'device_config'

TEMPLATE = templates.devices

# Device property keys
DEV_IP = u'ip'
DEV_PORT = u'port'
DEV_ACTIVE = u'active'
DEV_DEFAULT = u'default'


def _register_device_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=DEVICE_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=schema.devices)

    return cfg


# TODO: this previously returned a list!
def get_devices(active_devices_only=False):

    _register_device_config()

    cfg = Configuration()

    devices = cfg.find(DEVICE_CONFIG, [(u'active', True)]) if active_devices_only else cfg[DEVICE_CONFIG]

    return devices


# TODO: this previously returned a list!
def get_active_devices():
    return get_devices(active_devices_only=True)


def get_device(device=None,
               active_devices_only=False,
               suppress_refetch=False):

    try:
        # in case we already have the device,
        # use it's device field for the re-fetch
        # Could just return it, but fetching again
        # will pull changes from the DB
        # since the last fetch.  TODO: is this not the point? Keep everything up to date?
        device[DEVICE]
        if suppress_refetch:
            return device
        device = device[DEVICE]
    except Exception as e:
        pass

    if not device:
        return get_default_device()

    db = ConfigurationDB()
    db.open()

    where_clause = []

    if device is not None:
        where_clause.append({u'column': DEVICE,
                             u'value':    device,
                             u'operator': u'='})

    if active_devices_only:
        where_clause.append({u'column': ACTIVE,
                             u'value':     u'*',
                             u'operator':  u'=',
                             u'condition': u'AND'})

    matched_device = db.get_formatted_row(table = DEVICE_TABLE,
                                          where = where_clause)
    if not matched_device:
        # No match for DEVICE, try DEVICE_ID

        where_clause = [{u'column': DEVICE_ID,
                         u'value':   device,
                         u'operator': u'='}]

        if active_devices_only:
            where_clause.append({u'column': ACTIVE,
                                 u'value':     u'*',
                                 u'operator':  u'=',
                                 u'condition': u'AND'})

        matched_device = db.get_formatted_row(table = DEVICE_TABLE,
                                              where = where_clause)
        if not matched_device:
            if active_devices_only:
                raise LookupError(u'Device "{device}" is not active!'
                                  .format(device = device))
            else:
                raise LookupError(u'Device "{device}" is not configured!'
                                  .format(device = device))

    logging.debug(matched_device)

    db.close()

    return matched_device


def get_active_device(device=None):
    return get_device(device=device,
                      active_devices_only=True)

print get_device()
print get_active_device()

"""
# TODO
def get_default_device():

    db = ConfigurationDB()
    db.open()

    count = db.get_table_row_count(table = DEVICE_TABLE,
                                   where = [{u'column': DEFAULT_DEVICE,
                                             u'value':    u'*',
                                             u'operator': u'='}])
    if count == 1:

        device = db.get_formatted_row(table = DEVICE_TABLE,
                                      where = [{u'column': DEFAULT_DEVICE,
                                                u'value':    u'*',
                                                u'operator': u'='}])
        logging.debug(device)

    elif count == 0:
        set_first_configured_device_as_default()
        return get_default_device()
    else:
        raise LookupError(u'More than one default Device is configured!')

    db.close()

    return device


# TODO
def get_default_device_or_first_configured():

    """"""
    Attempts to retrieve the default device.
    If no default device configured then it will return the first active device.
    If no active devices then it will return the first device it can get!
    @return:
    """"""

    try:
        return get_default_device()

    except LookupError:

        try:
            return get_active_devices()[0]

        except IndexError:
            return get_devices()[0]


# TODO
def delete_device(device):

    db = ConfigurationDB()
    db.open()

    count = db.get_table_row_count(table=DEVICE_TABLE,
                                   where=[{u'column': DEVICE,
                                           u'value':    device,
                                           u'operator': u'='}])

    if count == 1:
        db.delete(table=DEVICE_TABLE,
                  where=[{u'column': DEVICE,
                          u'value':    device,
                          u'operator': u'='}])
        db.save()

    elif count == 0:
        raise LookupError(u'Device does not exist!')

    else:
        raise LookupError(u'Not deleting as more than one device found!')

    db.close()


# TODO
def update_device(device):

    db = ConfigurationDB()
    db.open()

    logging.debug(device)

    if device.get(DEVICE):

        # Get table headings
        db.select(table = DEVICE_TABLE)
        columns = db.get_table_headings()
        logging.debug(columns)

        # Setup values
        values = {}
        for column in columns:
            if column in device:
                values[column] = device.get(column)

        logging.debug(values)

        # Update record
        db.update_record(table=DEVICE_TABLE,
                         values = values,
                         where = [{u'column': DEVICE,
                                   u'value':    device[DEVICE],
                                   u'operator': u'='}])
    else:
        raise ValueError(u"Missing required key: u'device'!")

    db.save()
    db.close()


# TODO
def set_first_configured_device_as_default():

    devices = get_devices()

    for device in devices:
        device[DEFAULT_DEVICE] = False

    devices[0][DEFAULT_DEVICE] = True
    update_device(devices[0])


def get_hostname(device,
                 api,
                 environment,
                 hostname=None):

    if hostname:  # TODO: WTF?  Why would we be getting the hostname if we already have it?
        return hostname

    endpoint = Endpoints().get_endpoint(api=api,
                                        environment=device[environment])

    if endpoint.port:
        return u'{hostname}:{port}'.format(hostname=endpoint.hostname,
                                           port=endpoint.port)

    return endpoint.hostname
"""