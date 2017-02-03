#!/usr/bin/env python
# encoding: utf-8
"""
    Copyright 2016 Scott Doucet

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
import json
import ast
import yaml


class trabConfig():
    """
        trabConfig
        ==========

        Arguments
        ---------
          path:        Path to settings file
          autosave:    Save after every modification to settings. False by default.
          data:        Config file format. ie: dict or yaml. Defaults to dict.

        Methods
        -------

          get(key)         # Returns setting if it exists else returns False
          set(key, value)  # Set a new value in config
          new(key, value)  # Set the value of a setting if it exists else returns False
          delete(key)      # Deletes setting if it exists else returns False
          save()           # Save the config file.
          items()          # Returns the items in the config file.
          keys()           # Returns a list of the keys in the config file.
          values()         # Returns a list of the values in the config file.

        Initialization is as easy as -

            import trabConfig

            config_file = "MyConfig.cfg"
            config = trabConfig(config_file, autosave=False, config_format='dict')

        Notes -

            supports item assignment, ie: `config[key] = value`


        Created by - traBpUkciP 2016-2017

    """

    def __init__(self, path, autosave=False, data="dict"):
        self._file_path = path
        self.auto_save = autosave
        self._format = data
        self._config_data = {}
        self._load_cfg()

    def get(self, key, d=None):
        return self._config_data.get(key, d)

    def set(self, key, value):
        if key in self._config_data:
            self._config_data[key] = value
            if not self.auto_save:
                return
            self.save()
        else:
            raise KeyError

    def new(self, key, value):
        if key not in self._config_data:
            self._config_data[key] = value
            if not self.auto_save:
                return
            self.save()

    def save(self):
        self._save_cfg()

    def delete(self, key):
        self._config_data.pop(key, None)
        if self.auto_save:
            self.save()

    def items(self):
        return self._config_data.items()

    def keys(self):
        return self._config_data.keys()

    def values(self):
        return [self._config_data[key] for key in self._config_data]

    def __contains__(self, item):
        return item in self._config_data

    def __repr__(self):
        return repr(self._config_data)

    def __getitem__(self, item):
        return self._config_data[item]

    def __setitem__(self, key, value):
        self._config_data[key] = value

    def _load_from_dict(self):
        with open(self._file_path, 'rb') as f:
            try:
                self._config_data = ast.literal_eval(f.read())
            except SyntaxError:
                return

    def _load_from_yaml(self):
        with open(self._file_path, 'rb') as f:
            try:
                self._config_data = yaml.safe_load(f.read())
            except SyntaxError:
                return

    def _load_cfg(self):
        formats = {
            "dict": self._load_from_dict,
            "yaml": self._load_from_yaml,
        }
        return formats[self._format]()

    def _save_to_dict(self):
        with open(self._file_path, 'wb') as f:
            f.write(json.dumps(self._config_data))

    def _save_to_yaml(self):
        with open(self._file_path, 'wb') as f:
            f.write(yaml.safe_dump(self._config_data))

    def _save_cfg(self):
        formats = {
            "dict": self._save_to_dict,
            "yaml": self._save_to_yaml,
        }
        formats[self._format]()
