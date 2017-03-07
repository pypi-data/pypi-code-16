"""
This module contain helpers to parse the settings
"""
import datetime
import re

CSTT_REGEX = re.compile(r'((?P<hours>[0-9]+?)(hr|h))?((?P<minutes>[0-9]+?)m)?((?P<seconds>[0-9]+?)s)?')


class ConfigurationVariable:
    """Abstract validation of configuration variable"""

    def __init__(self, name: str, var_type, convert_func=None, validation_func=None):
        self.name = name
        self.type = var_type

        self.convert_func = convert_func
        self.validation_func = validation_func

        self.value = None
        self.validated = False
        self.convert_func_executed = False

    def validate(self):
        """Execute validation"""
        if callable(self.validation_func):
            self.validated = self.validation_func(self)
        else:
            self.validated = isinstance(self.value, self.type)

        if callable(self.convert_func) and not self.convert_func_executed and not self.validated:
            self.value = self.convert_func(self.value)
            self.convert_func_executed = True
            self.validate()


def convert_string_to_timedelta(time_str: str):
    """Convert strings like 1hr1m1s"""
    parts = CSTT_REGEX.match(time_str)
    if not parts:
        raise ValueError('Cannot parse {time_str} into timedelta'.format(time_str=time_str))
    parts = parts.groupdict()
    parts = {key: value for (key, value) in parts.items() if value is not None}
    if len(parts) is 0:
        raise ValueError('Cannot parse {time_str} into timedelta'.format(time_str=time_str))
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return datetime.timedelta(**time_params)


def convert_string_to_debug_level(debug_level_str: str):
    """Convert a string containing a debug level known in the logging module to corresponding representation of the logging module"""
    if not isinstance(debug_level_str, str):
        return debug_level_str

    levels = [
        'CRITICAL',
        'ERROR',
        'WARNING',
        'INFO',
        'DEBUG',
        'NOTSET'
    ]

    if debug_level_str.upper() not in levels:
        raise ValueError('Unknown debug level string "{value}" given. Supported are: {levels}'.format(value=debug_level_str, levels=', '.join(levels)))

    import logging
    return getattr(logging, debug_level_str.upper())


def convert_string_to_list(val: str):
    """Split a string by the delimiter ',' and strip white space of each element"""
    if not isinstance(val, str):
        return val
    tmp_list = val.split(',')

    ret = []
    for val in tmp_list:
        ret.append(val.strip())

    return ret


def check_pi_pin_board_range(conf_var: ConfigurationVariable):
    """Check the value of the given configuration variable is valid gpio pin of the raspberry pi 3"""
    pin = conf_var.value
    pi_output_pin_list = [
        3, 5, 7,
        11, 13, 15,
        19, 21, 23,
        27, 29, 31,
        33, 35, 37,
        8, 10, 12,
        16, 18,
        22, 24, 26,
        28, 32, 36,
        38, 40
    ]

    return pin in pi_output_pin_list


def check_list_of_strings(conf_var: ConfigurationVariable):
    """Check the value of the configuration is a list and only contains strings"""
    val = conf_var.value
    if not isinstance(conf_var.value, list):
        return False

    for item in val:
        if not isinstance(item, str):
            return False

    return True
