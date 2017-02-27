# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys
import os
from os.path import join, exists

from .fixtures import appengine


def find_appengine_sdk():
    sdk_files = [
        'dev_appserver.py',
        'appcfg.py',
        'google',
        'lib',
    ]
    paths = sys.path + os.environ.get('PATH').split(':')
    is_sdk = lambda path: all(exists(join(path, f)) for f in sdk_files)
    return next((path for path in paths if is_sdk(path)), None)


def setup_appengine_devenv(sdk_path=None):
    sys.path.insert(0, sdk_path)

    import dev_appserver
    dev_appserver.fix_sys_path()

    import google.appengine.tools.os_compat


def pytest_addoption(parser):
    sdk_path = os.environ.get('APPENGINE_SDK')
    if sdk_path is None:
        sdk_path = find_appengine_sdk()

    print("\033[32mSetting up AppEngine dev env: \033[33m{}\033[0m".format(
        sdk_path
    ))
    setup_appengine_devenv(sdk_path)
