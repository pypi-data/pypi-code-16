"""Logging configuration."""

import logging
import logging.config

# Name the logger after the package.
logger = logging.getLogger(__package__)


def set_verbose(verbose: bool):
    if verbose:
        logging.basicConfig(level=logging.INFO)
