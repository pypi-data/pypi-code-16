# coding=utf-8
__author__ = 'Maple.Liu'
import importlib
import os
from base_bridge.utils.http import response_as_json

def get_settings():
    settings_module = os.environ['DJANGO_SETTINGS_MODULE']
    settings = importlib.import_module(settings_module)
    return settings

