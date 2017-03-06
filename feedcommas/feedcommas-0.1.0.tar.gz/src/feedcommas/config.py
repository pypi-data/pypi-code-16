# Copyright (C) 2017 Michał Góral.
#
# This file is part of Feed Commas
#
# Feed Commas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Feed Commas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Feed Commas. If not, see <http://www.gnu.org/licenses/>.

'''Reader and handler of globally-available app configuration.'''

import os
import configparser

from collections import OrderedDict

import mgcomm.xdg
import mgcomm.env

from feedcommas.utils import mkdir_p

_cfg = None

_defaults = OrderedDict((
    ('server', OrderedDict((
        ('address', 'https://commafeed.com'),
        ('username', ''),
        ('password', ''),
        ('password-cmd', ''),
        ('workers', '2'),
    ))),

    ('keys', OrderedDict((
        ('nav-down', 'j'),
        ('nav-up', 'k'),
        ('nav-right', 'l'),
        ('nav-left', 'h'),
        ('open-browser', 'c-]'),
        ('toggle-read', 'r'),
        ('toggle-star', 's'),
        ('show-all', ''),
        ('show-unread', ''),
        ('refresh', 'f5'),
        ('sync', ''),
        ('quit', 'q'),
    ))),

    ('settings', OrderedDict((
        ('mark-read-time', '2'),
        ('show-read', 'false'),
        ('supported-colors', '256'),
        ('bright-bold', 'false'),
        ('html-filter', 'builtin'),
        ('cache-time', '0'),
    ))),

    ('colors', OrderedDict((
        ('article-title', 'yellow'),
        ('article-title-focus', 'light blue'),
        ('article-border-focus', 'light blue'),
        ('metadata', 'light gray'),
        ('menu-focus-fg', 'white'),
        ('menu-focus-bg', 'light blue'),
        ('menu-line', 'dark gray'),
        ('menu-selected', 'light red'),
        ('error-fg', 'white'),
        ('error-bg', 'dark red'),
    ))),
))


def config_path():
    '''Returns a path to the configuration file, which is searched in a way
    specified by XDG Base Directory Specification:
    https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

    This function doesn't ensure that configuration file indeed exists. If no
    suitable configuration exists, it returns a user-specific path which is best
    suitable (according to XDG spec).'''
    app_name = 'feed-commas'
    cfg_name = 'config.ini'

    default_cfg_dir = os.path.join(mgcomm.env.home(), '.config')
    cfg_home = mgcomm.env.var_split('XDG_CONFIG_HOME', default_cfg_dir)[0]
    default_path = os.path.join(cfg_home, app_name, cfg_name)

    return mgcomm.xdg.config(app_name, cfg_name, default_path)


def config(section=None):
    '''Returns a global (shared) configuration object. If it hasn't been created
    yet, it is read from the mix of default values and configuration file.'''
    global _cfg  # pylint: disable=global-statement
    if _cfg is None:
        _cfg = configparser.ConfigParser()

        # this preserves the order of configuration file
        _cfg.read(config_path())
        for section, opts in _defaults.items():
            if not _cfg.has_section(section):
                _cfg.add_section(section)
            for option_name, value in opts.items():
                if not _cfg.has_option(section, option_name):
                    _cfg.set(section, option_name, value)
    return _cfg


def write_config(cfg):
    '''Writes back any changes in configuration to the file. If there's no
    configuration under a `config_path()`, creates one.'''
    cfg_path = config_path()
    mkdir_p(os.path.dirname(cfg_path))
    with open(cfg_path, 'w') as configfile:
        cfg.write(configfile)


def get_value(section, field_name, default, type_=str):
    '''Properly returns a value of the field, even if it isn't set or is set to
    an empty value (empty string).'''
    assert type_ == type(default)
    ret = section.get(field_name)
    if not ret:
        ret = default
    return type_(ret)
