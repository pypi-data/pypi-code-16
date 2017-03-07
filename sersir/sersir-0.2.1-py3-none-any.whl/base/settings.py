"""Parse and provide the configuration for sersir"""
import datetime
import os
import warnings

from sersir.utils import Map
from sersir.utils.setting_helper import \
    ConfigurationVariable, \
    convert_string_to_timedelta, \
    convert_string_to_list, \
    convert_string_to_debug_level, \
    check_list_of_strings, \
    check_pi_pin_board_range

# Try to import legacy config file
try:
    from sersir import config as legacy
except ImportError:
    legacy = {}

try:
    settings_module = os.environ.get('SERSIR_SETTINGS_MODULE', {})
    if isinstance(settings_module, str):
        from importlib import import_module

        settings_module = import_module(settings_module)
except ImportError as exception:
    settings_module = {}
    warnings.warn(exception)

configuration_variables = [
    ConfigurationVariable('scheme', str),
    ConfigurationVariable('host', str),
    ConfigurationVariable('path', str),
    ConfigurationVariable('user', str),
    ConfigurationVariable('token', str),
    ConfigurationVariable('sleep_time', datetime.timedelta, convert_func=convert_string_to_timedelta),
    ConfigurationVariable('audit_log_file', str),
    ConfigurationVariable('state_file', str),
    ConfigurationVariable('debug_level', int, convert_func=convert_string_to_debug_level),
    ConfigurationVariable('lamp_gpio_board_pin', int, convert_func=int, validation_func=check_pi_pin_board_range),
    ConfigurationVariable('ignored_projects', list, convert_func=convert_string_to_list, validation_func=check_list_of_strings)
]

conf = Map()

for conf_var in configuration_variables:
    name = conf_var.name
    if 'SERSIR_' + name.upper() in os.environ:
        conf_var.value = os.environ.get('SERSIR_' + name.upper(), None)
    elif hasattr(settings_module, name):
        conf_var.value = getattr(settings_module, name)
    elif hasattr(legacy, name):
        conf_var.value = getattr(legacy, name)
    else:
        raise RuntimeError('Configuration variable {} not set'.format(name))

    conf_var.validate()

    if conf_var.validated:
        conf[conf_var.name] = conf_var.value
    else:
        raise ValueError('The value "{value}" of the configuration variable "{name}" could not be validated'.format(name=name, value=conf_var.value))
