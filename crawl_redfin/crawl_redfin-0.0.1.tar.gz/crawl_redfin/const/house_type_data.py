#!/usr/bin/env python
# -*- coding: utf-8 -*-

from crawl_redfin.pkg.autocompvar.metadata import gen_code
from crawl_redfin.pkg.dataIO import textfile


metadata = {
    "classname": "HouseTypeCollection",
    "attrs": [],
    "collection": [
        {
            "classname": "HouseType",
            "attrs": ["id", "name"],
            "keys": ["id", "name"],
            "data": {"id": 1, "name": "Single House"},
        },
        {
            "classname": "HouseType",
            "attrs": ["id", "name"],
            "keys": ["id", "name"],
            "data": {"id": 2, "name": "Condo"},
        },
        {
            "classname": "HouseType",
            "attrs": ["id", "name"],
            "keys": ["id", "name"],
            "data": {"id": 3, "name": "Town House"},
        },
        {
            "classname": "HouseType",
            "attrs": ["id", "name"],
            "keys": ["id", "name"],
            "data": {"id": 4, "name": "Multi Family"},
        },
        {
            "classname": "HouseType",
            "attrs": ["id", "name"],
            "keys": ["id", "name"],
            "data": {"id": 5, "name": "Land"},
        },
        {
            "classname": "HouseType",
            "attrs": ["id", "name"],
            "keys": ["id", "name"],
            "data": {"id": 6, "name": "Other Type"},
        },
    ],
}

if __name__ == "__main__":
    code = gen_code(metadata)
    textfile.write(code, "house_type.py")