
# Get module version
from _metadata import __version__

# Import key items from module
from configurationutil.configuration import (
    Configuration
)

from configurationutil.cfg_objects.json_config import (
    JSONConfig
)

import configurationutil.configuration as cfg_params

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
