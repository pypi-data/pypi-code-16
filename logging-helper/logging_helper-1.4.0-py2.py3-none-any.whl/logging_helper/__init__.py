
# Get module version
from _metadata import __version__

# Import key items from module
from logging_helper import *

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
