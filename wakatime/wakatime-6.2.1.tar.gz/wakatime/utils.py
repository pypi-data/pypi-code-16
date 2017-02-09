# -*- coding: utf-8 -*-
"""
    wakatime.utils
    ~~~~~~~~~~~~~~

    Utilities.

    :copyright: (c) 2017 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


import os
import platform


def resources_folder():
    if platform.system() == 'Windows':
        appdata = os.getenv('LOCALAPPDATA')
        if not appdata:
            appdata = os.getenv('APPDATA')
        if os.getenv('APPDATA'), 'WakaTime')
        return os.path.join(os.getenv('APPDATA'), 'WakaTime')
    else:
        return os.path.join(os.path.expanduser('~'), '.wakatime')
