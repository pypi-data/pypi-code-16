#!/usr/bin/env python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import collections
import traceback
from configparser import ConfigParser

from gateway_helpers import get_instrument
from gateway_helpers import get_logger
from gateway_helpers import post_alert
from gateway_helpers import print_debug

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']
DEFAULT_TEK_TYPE = 'TektronixMDO3012'

logger = get_logger(
    log_filename=CLIENT_SETTINGS['DEFAULT_LOGFILE'])


def reset_scope(instrument_type=DEFAULT_TEK_TYPE):
    """Calls utility.reset() to reset scope"""
    try:
        instr = get_instrument({'instrument_type': instrument_type})
    except Exception:
        print_debug(traceback.format_exc(), post=True)
    try:
        instr.utility.reset()
        print_debug("instrument reset")
    except Exception:
        print_debug(traceback.format_exc(), post=True)
    finally:
        instr.close()


def check_scope(instrument_type=DEFAULT_TEK_TYPE):
    """Checks acquisition type to check if scope working"""
    acq_type = None
    try:
        instr = get_instrument({'instrument_type': instrument_type})
    except Exception:
        print_debug(traceback.format_exc(), post=True)
        return None
    try:
        acq_type = instr.acquisition.type
        acq_time_per_record = instr.acquisition.time_per_record
        trigger_type = instr.trigger.type
        trigger_coupling = instr.trigger.coupling
        print_debug("acq_type: " + acq_type)
        inst_info = {
            'acq_type': acq_type,
            'acq_time_per_record': acq_time_per_record,
            'trigger_type': trigger_type,
            'trigger_coupling': trigger_coupling,
        }
        print_debug("basic instrument info: %s" % inst_info, post=True)
        return acq_type
    except Exception:
        print_debug(traceback.format_exc(), post=True)
    finally:
        instr.close()
        return acq_type


def set_scope(scope_info=None):
    """Sets basic scope info to test scope"""
    scope_dict = collections.defaultdict(int)
    scope_dict.update(scope_info)
    if not scope_dict['instrument_type']:
        scope_dict['instrument_type'] = DEFAULT_TEK_TYPE
    try:
        instr = get_instrument(scope_dict)
    except Exception:
        print_debug(traceback.format_exc(), post=True)
        return None
    try:
        instr.acquisition.type = scope_dict['acq_type']
        instr.acquisition.time_per_record = scope_dict['acq_time_per_record']
        instr.trigger.type = scope_dict['trigger_type']
        instr.trigger.coupling = scope_dict['coupling']
        return True
    except Exception:
        print_debug(traceback.format_exc(), post=True)
        return None


def check_or_reset(session, command, instrument_type):
    """Runs ad hoc check or reset scope commands"""
    command_funcs = {
        'reset': reset_scope,
        'check': check_scope,
    }
    try:
        scope_info = command_funcs[command](instrument_type)
    except Exception:
        logger.error(traceback.format_exc())
        scope_info = None
    finally:
        post_alert(session, scope_info)
