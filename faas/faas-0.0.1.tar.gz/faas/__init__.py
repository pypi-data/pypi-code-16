# Set default logging handler to avoid "No handler found" warnings.
import logging
from .faas import Faas  # NOQA

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())
logger.setLevel(logging.INFO)
