import sys
import logging
import speedyio.interactive as speedyio

from bucketlist import configio, defaults
from bucketlist.errors import BucketlistError


appconfig = configio.Config()

SUPPORTED_PROVIDERS = [
    'wunderlist',
    'localfs'
]

provider_not_set_error = False
try:
    appconfig.get_provider_name()
except BucketlistError:
    provider_not_set_error = True

if not appconfig.config_exists() or provider_not_set_error is True:
    options = [speedyio.Item(provider, provider) for provider in SUPPORTED_PROVIDERS]

    provider_name = speedyio.chooseone(options, message="Which provider would you prefer?")
    appconfig.init(provider_name)

    speedyio.info("Please run following command to make sure everything is set\n    bucket-list init")

# Setting up IO
io = appconfig.get('io', 'mode') or defaults.IO_MODE
if io == 'basic':
    import speedyio.basic as speedyio
elif io == 'interactive':
    import speedyio.interactive as speedyio
else:
    import speedyio.basic as speedyio

# Setting up Logging
logger = logging.getLogger(__name__)

def configure_logger(logger):
    logfile = appconfig.get('logging', 'file') or defaults.LOG_FILE

    loglevel_map = {
        'error': logging.ERROR,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARN,
        'critical': logging.CRITICAL
    }

    loglevel_str = appconfig.get('logging', 'level') or defaults.LOG_LEVEL
    loglevel = loglevel_map.get(loglevel_str) or logging.ERROR
    logger.setLevel(loglevel)

    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(fh)


configure_logger(logger)
