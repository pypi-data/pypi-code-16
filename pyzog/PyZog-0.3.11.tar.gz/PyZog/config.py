#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

__author__ = "LaBatata (victor hugo gomes)"
__version__ = "0.3.11"
__email__ = "labatata101@gmail.com"


def get_home_path():
    return os.path.expanduser("~")


def dir_exist(path):
    return os.path.isdir(path)


def file_exist(path):
    return os.path.isfile(path)


def logged(logged=False):
    return logged


def create_conf_file(conf):
    with open(get_home_path() + '/.conf', 'w', encoding='utf8') as outfile:
        json.dump(conf, outfile, sort_keys=True, indent=4)


def load_conf_file():
    with open(get_home_path() + '/.conf', 'r', encoding='utf8') as keys:
        key = json.load(keys)
        return key
