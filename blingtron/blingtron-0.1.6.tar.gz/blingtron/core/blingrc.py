# -*- coding: utf-8 -*-
import json

from ..domain import blingrc
from ..domain.vendor import PackerConfigNotFound
from ..vendor.packer import read_config
from ..core.io import err

from ..config import config as app_conf


class BlingConfig(object):
    def __init__(self, config):
        self._config = config
        self.custom_keys = {
            'image_name': self.image_name,
        }

        self._config = self.custom_keys.copy()
        self._config.update(config)

    @property
    def config(self):
        return self._config.copy()

    @property
    def image_name(self):
        return '{registry}/{name}'.format(**self.config)

    def get(self, key, or_else=None):
        return self.config.get(key, or_else)


def open_config():
    config_file = app_conf.bling.config_path
    try:
        with open(config_file, 'rU') as f:
            data = json.load(f)
        for key, default in app_conf.bling.optional_keys.iteritems():
            if key not in data:
                data[key] = default
        return BlingConfig(data)
    except IOError:
        raise blingrc.MissingBlingConfig('cannot find "%s" config file' % config_file)
    except ValueError as e:
        raise blingrc.MalformedBlingConfig('malformed json in "%s"\n%s' % (config_file, e))


def _validate_config(config):
    errors = []
    for key in app_conf.bling.required_keys:
        if key in config.config.keys():
            continue
        errors.append('expected key: "%s" key (not found)' % key)
    try:
        read_config(config.get('packer', ''))
    except PackerConfigNotFound as e:
        errors.append('%s (packer missing)' % e)
    return blingrc.ConfigValidation(errors=errors, config=config)


def validate_config(config):
    validation = _validate_config(config)
    if not validation.has_error:
        return True
    else:
        [err(error, exit_=False) for error in validation.errors]
        return False


def patch_environ(environ, config):
    environ = environ.copy()
    environ.update({k: str(v) for k, v in config.iteritems()})
    return environ
