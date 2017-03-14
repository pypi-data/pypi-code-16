#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#--------------

"""
Implementation of JSON configuration handler.

This module provides following tools and features:

* Simple writing of formated JSON configuration files
* Simple reading of any JSON configuration files
* Reading and merging of multiple JSON configuration files/directories
* Support for comments
* JSON schema validation
"""

import os
import json
from jsonschema import Draft4Validator, FormatChecker

class JSONSchemaException(Exception):
    """
    Exception describing JSON schema problems.

    This exception will be thrown, when JSON schema validation fails.
    """
    def __init__(self, errstr, errlist):
        self.errstr  = errstr
        self.errlist = errlist
    def __str__(self):
        return repr(self.errstr)

def sortkey(k):
    """
    Helper method for sorting JSON paths.

    Treat keys as lowercase, prefer keys with less path segments.
    """
    return (len(k.path), "/".join(str(k.path)).lower())

def json_default(o):
    """
    Fallback method for serializing unknown objects into JSON.
    """
    return str(o)

#-------------------------------------------------------------------------------

def json_save(json_file, data, **kwargs):
    """
    Save data structure into given JSON configuration file.
    """
    if not 'sort_keys' in kwargs:
        kwargs['sort_keys'] = True
    if not 'indent' in kwargs:
        kwargs['indent'] = 4
    if not 'default' in kwargs:
        kwargs['default'] = json_default
    with open(json_file, "w") as f:
        json.dump(data, f, **kwargs)

def json_load(json_file):
    """
    Load contents of given JSON configuration file.

    The JSON syntax is enhanced with support for single line comments ('#','//').
    """
    with open(json_file, "r") as f:
        contents = "\n".join((l for l in f if not l.lstrip().startswith(("#", "//"))))
        return json.loads(contents)

def config_validate(config, schema):
    """
    Perform json schema validation of given object, raise JSONSchemaException
    in case of any validation error.
    """
    if not isinstance(schema, dict):
        raise JSONSchemaException("Validation error: Schema parameter must be a dictionary structure", ["Schema parameter must be a dictionary structure"])

    # Validate the structure of the schema itself
    Draft4Validator.check_schema(schema)

    # Perform the validation and format errors to be more readable
    validator = Draft4Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(config), key=sortkey):
        errors.append(
            "JSON schema validation error: key \"%s\", value \"%s\", expected - %s, error message - %s\n" % (
                u"/".join(str(v) for v in error.path),
                error.instance,
                error.schema.get('description', '(no additional info)'),
                error.message
            )
        )
    # Raise custom exception in case of any error
    if len(errors):
        raise JSONSchemaException("\n".join(errors), errors)

    return True

def config_load(config_file, schema = None):
    """
    Load configuration from given JSON configuration file with optional JSON
    schema validation.
    """
    config = json_load(config_file)
    if schema:
        # If the schema parameter is boolean, generate the name of the schema
        # file from the name of configuration file
        if isinstance(schema, bool):
            schema = "{}.schema".format(config_file)
        if isinstance(schema, str):
            # If the schema parameter is string and it is the name of
            # existing directory, look for appropriate schema file in that
            # directory.
            if os.path.isdir(schema):
                schema = os.path.join(schema, "{}.schema".format(os.path.basename(config_file)))
            # If the schema parameter is string and it is the name of
            # existing file, load the schema definitions from that file
            if os.path.isfile(schema):
                schema = json_load(schema)
        if not isinstance(schema, dict):
            raise JSONSchemaException("Validation error: Schema parameter must be either boolean, string name of schema file or directory, or dictionary structure", ["Schema parameter must be either boolean, string name of schema file or directory, or dictionary structure"])
        config_validate(config, schema)
    return config

def config_load_n(config_files, schema = None):
    """
    Load configuration from multiple JSON configuration files with optional JSON
    schema validation.
    """
    config = {}
    for cf in config_files:
        c = config_load(cf, schema = schema)
        config.update((k, v) for k, v in c.items() if v is not None)
    return config

def config_load_dir(config_dir, schema = None, extension = '.json.conf'):
    """
    Load configuration from multiple JSON configuration files with optional JSON
    schema validation.
    """
    config_files = []
    all_files = os.listdir(config_dir)
    for f in sorted(all_files):
        fn = os.path.join(config_dir, f)
        if not os.path.isfile(fn):
            continue
        if not fn.endswith(extension):
            continue
        config_files.append(fn)
    return config_load_n(config_files, schema)

if __name__ == "__main__":
    """
    Perform the demonstration.
    """
    import pprint

    print("Loading single JSON config file:")
    #cfg_a = config_load("/tmp/demo.pyzenkit.jsonconf.json")
    #pprint.pprint(cfg_a)

    print("Loading single JSON config file with autovalidation:")
    #cfg_a = config_load("/tmp/demo.pyzenkit.jsonconf.json", schema = True)
    #pprint.pprint(cfg_a)

    print("Loading JSON config directory:")
    #cfg_b = config_load_dir("/tmp/demo.pyzenkit.jsonconf/")
    #pprint.pprint(cfg_b)

    print("Loading JSON config directory with autovalidation:")
    #cfg_b = config_load_dir("/tmp/demo.pyzenkit.jsonconf/", schema = True)
    #pprint.pprint(cfg_b)
