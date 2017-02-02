#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2016 DataONE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module object_format_info
============================

:Synopsis:
  Map DataONE ObjectFormatIDs to Content-Type and filename extension. The
  mappings are provided in a CSV file. Raises KeyError for unknown values.
:Created: 2012-10-25
:Author: DataONE (Dahl)
"""

# Stdlib
import csv
import os


def make_absolute(p):
  return os.path.join(os.path.abspath(os.path.dirname(__file__)), p)

# Config
MIME_MAPPINGS_CSV_PATH = make_absolute('mime_mappings.csv')


class Singleton(object):
  _instances = {}

  def __new__(class_, *args, **kwargs):
    if class_ not in class_._instances:
      class_._instances[class_] = super(Singleton, class_)\
        .__new__(class_, *args, **kwargs)
    return class_._instances[class_]

#===============================================================================


class ObjectFormatInfo(Singleton):
  def __init__(self, csv_file=None):
    if csv_file is None:
      self.csv_file = open(MIME_MAPPINGS_CSV_PATH)
    else:
      self.csv_file = csv_file
    self.read_csv_file()

  def content_type_from_format_id(self, format_id):
    return self.format_id_map[format_id][0]

  def filename_extension_from_format_id(self, format_id):
    return self.format_id_map[format_id][1]

  def read_csv_file(self, csv_file=None):
    """Reinitialize the map from a csv file object"""
    if csv_file is not None:
      self.csv_file = csv_file
    self._read_format_id_map_from_file()

  #
  # Private.
  #

  def _read_format_id_map_from_file(self):
    self.csv_file.seek(0)
    csv_reader = csv.reader(self.csv_file)
    try:
      self.format_id_map = dict((r[0], r[1:]) for r in csv_reader)
    except (csv.Error, Exception) as e:
      raise Exception(
        'Error in csv file. Line: {1}  Error: {2}'.format(csv_reader.line_num, e)
      )
