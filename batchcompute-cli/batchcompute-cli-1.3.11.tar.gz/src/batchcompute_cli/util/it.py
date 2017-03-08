from ..const import *
from . import client

def list():
    arr = client.list_instance_types()
    return arr

def list_spot():
    arr = client.list_spot_instance_types()
    return arr or []


def get_ins_type_map():
    arr = list()
    arr2 = list_spot()
    m = {}
    for item in arr:
        m[item['name']] = item
    for item in arr2:
        m[item['name']] = item
    return m
