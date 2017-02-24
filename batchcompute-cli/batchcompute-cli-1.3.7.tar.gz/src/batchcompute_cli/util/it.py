from ..const import *
from . import client

def list():
    arr = client.list_instance_types()
    return arr


def get_ins_type_map():
    arr = list()
    m = {}
    for item in arr:
        m[item['name']] = item
    return m


