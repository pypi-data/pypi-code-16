# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Configuration tools."""


import os
import types


class Config(dict):
    """Implements a dictionary with advanced features."""

    def __init__(self, path=None, default=None):
        """initialization.

        Args:
            path: the directory to search for configuration files.
            default: default values in the form of a dictionary.
        """
        dict.__init__(self, default or {})
        self.root_path = path or '.'

    def from_object(self, obj):
        """Load configuration from a python object."""
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_pyfile(self, filename, silent=False):
        """Load a configuration file."""
        filename = os.path.join(self.root_path, filename)
        d = types.ModuleType('config')
        d.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            if not silent:
                e.strerror = 'File not found (%s).' % e.strerror
                raise
        self.from_object(d)

    def from_envvar(self, name, silent=False):
        """Load a configuration file from an environment variable."""
        rv = os.environ.get(name)
        if not rv and not silent:
            err_msg = '%s environment variable is not set.'
            raise RuntimeError(err_msg % name)
        elif rv:
            self.from_pyfile(rv, silent=silent)

    def get_namespace(self, namespace, trim=True):
        """Get a namespace sub-configuration.

        Args:
            namespace: the target namespace.
            trim: trim the namespace from each key.

        Returns: a dictionary
        """
        return {k[(int(trim) * len(namespace)):].lstrip('_'): v for k, v
                in self.items() if k.startswith(namespace)}
