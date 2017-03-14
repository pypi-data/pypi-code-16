#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2016 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations

import logging

from logging_mv_integrations.tune_logging_handler import (get_tune_logger_with_handler)
from logging_mv_integrations import (TuneLoggingFormat)


def get_logger(
    logger_version,
    logger_format=TuneLoggingFormat.JSON,
    logger_name=None,
    module_name=None,
    logger_level=logging.NOTSET,
    logger=None
):

    if not logger_format:
        raise ValueError("Undefined 'logger_format'")
    if not logger_version:
        raise ValueError("Undefined 'logger_version'")

    if logger_name is None:
        if module_name is not None:
            logger_name = get_logger_name(module_name=module_name)
        else:
            logger_name = get_logger_name(module_name=__name__)

    return get_tune_logger_with_handler(
        logger_name=logger_name, logger_version=logger_version, logger_format=logger_format, logger_level=logger_level
    )


def get_logger_name(module_name):
    logger_name_parts = module_name.split('.')
    logger_name = logger_name_parts[0]
    if len(logger_name_parts) > 0:
        logger_name += '.' + logger_name_parts[-1]

    return logger_name
