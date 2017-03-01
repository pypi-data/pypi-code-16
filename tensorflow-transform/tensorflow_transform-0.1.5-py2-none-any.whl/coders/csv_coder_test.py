# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tensorflow-transform CsvCoder tests."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pickle

import numpy as np
import tensorflow as tf
from tensorflow_transform.coders import csv_coder
from tensorflow_transform.tf_metadata import dataset_schema

import unittest


class TestCSVCoder(unittest.TestCase):


  _COLUMNS = ['numeric1', 'text1', 'category1', 'idx', 'numeric2', 'value',
              'numeric3']
  # The following input schema has no default values, so any invocations to
  # decode with missing values should raise an error. CsvCoderDecodeTest adds
  # good coverage for missing value handling.
  _INPUT_SCHEMA = dataset_schema.from_feature_spec({
      'numeric1': tf.FixedLenFeature(shape=[], dtype=tf.int32),
      'numeric2': tf.VarLenFeature(dtype=tf.float32),
      'numeric3': tf.FixedLenFeature(shape=[1], dtype=tf.int32),
      'text1': tf.FixedLenFeature(shape=[], dtype=tf.string),
      'category1': tf.VarLenFeature(dtype=tf.string),
      'y': tf.SparseFeature('idx', 'value', tf.float32, 10),
  })

  def _assert_encode_decode(self, coder, data, expected_decoded):
    decoded = coder.decode(data)
    self.assertEqual(decoded, expected_decoded)

    encoded = coder.encode(decoded)
    self.assertEqual(encoded, data)

    decoded_again = coder.decode(encoded)
    self.assertEqual(decoded_again, expected_decoded)

  def test_csv_coder(self):
    data = '12,"this is a ,text",female,1,89.0,12.0,14'

    coder = csv_coder.CsvCoder(self._COLUMNS, self._INPUT_SCHEMA)

    # Python types.
    expected_decoded = {'category1': ['female'],
                        'numeric1': 12,
                        'numeric2': [89.0],
                        'numeric3': [14.0],
                        'text1': 'this is a ,text',
                        'y': ([12.0], [1])}
    self._assert_encode_decode(coder, data, expected_decoded)

    # Numpy types.
    expected_decoded = {'category1': np.array(['female']),
                        'numeric1': np.array(12),
                        'numeric2': np.array([89.0]),
                        'numeric3': np.array([14.0]),
                        'text1': np.array(['this is a ,text']),
                        'y': (np.array([12.0]), np.array(1))}
    self._assert_encode_decode(coder, data, expected_decoded)

  def test_tsv_coder(self):
    data = '12\t"this is a \ttext"\tfemale\t1\t89.0\t12.0\t14'

    coder = csv_coder.CsvCoder(self._COLUMNS, self._INPUT_SCHEMA,
                               delimiter='\t')
    expected_decoded = {'category1': ['female'],
                        'numeric1': 12,
                        'numeric2': [89.0],
                        'numeric3': [14],
                        'text1': 'this is a \ttext',
                        'y': ([12.0], [1])}
    self._assert_encode_decode(coder, data, expected_decoded)

  def test_valency(self):
    data = '11|12,"this is a ,text",female|male,1|3,89.0|91.0,12.0|15.0,14'
    feature_spec = self._INPUT_SCHEMA.as_feature_spec().copy()
    feature_spec['numeric1'] = tf.FixedLenFeature(shape=[2], dtype=tf.int32)
    schema = dataset_schema.from_feature_spec(feature_spec)
    multivalent_columns = ['numeric1', 'numeric2', 'y']
    coder = csv_coder.CsvCoder(self._COLUMNS, schema,
                               delimiter=',', secondary_delimiter='|',
                               multivalent_columns=multivalent_columns)
    expected_decoded = {'category1': ['female|male'],
                        'numeric1': [11, 12],
                        'numeric2': [89.0, 91.0],
                        'numeric3': [14],
                        'text1': 'this is a ,text',
                        'y': ([12.0, 15.0], [1, 3])}
    self._assert_encode_decode(coder, data, expected_decoded)

  # Test successful decoding with a single column.
  def testDecode(self):
    cases = [
        # FixedLenFeature scalar int.
        ('12', 12,
         tf.FixedLenFeature(shape=[], dtype=tf.int32)),
        # FixedLenFeature scalar float without decimal point.
        ('12', 12,
         tf.FixedLenFeature(shape=[], dtype=tf.float32)),
        # FixedLenFeature scalar float with decimal point.
        ('12.0', 12,
         tf.FixedLenFeature(shape=[], dtype=tf.float32)),
        # FixedLenFeature scalar float with quoted value.
        ('"12.0"', 12,
         tf.FixedLenFeature(shape=[], dtype=tf.float32)),
        # FixedLenFeature 1-d vector int.
        ('12', [12],
         tf.FixedLenFeature(shape=[1], dtype=tf.int32)),
        # FixedLenFeature unquoted text
        ('this is unquoted text', 'this is unquoted text',
         tf.FixedLenFeature(shape=[], dtype=tf.string)),
        # FixedLenFeature quoted text
        ('"this is a ,text"', 'this is a ,text',
         tf.FixedLenFeature(shape=[], dtype=tf.string)),
        # FixedLenFeature scalar numeric with default value.
        ('4', 4,
         tf.FixedLenFeature(shape=[], dtype=tf.int32, default_value=-1)),
        # FixedLenFeature scalar numeric with missing value and default value.
        ('', -1,
         tf.FixedLenFeature(shape=[], dtype=tf.int32, default_value=-1)),
        # FixedLenFeature scalar text with default value set.
        ('a test', 'a test',
         tf.FixedLenFeature(shape=[], dtype=tf.string, default_value='d')),
        # FixedLenFeature scalar text with missing value and default value set.
        ('', 'd',
         tf.FixedLenFeature(shape=[], dtype=tf.string, default_value='d')),
        # VarLenFeature text.
        ('a test', ['a test'], tf.VarLenFeature(dtype=tf.string)),
        # VarLenFeature text with missing value.
        ('', [],
         tf.VarLenFeature(dtype=tf.string)),
        # SparseFeature float one value.
        ('5,2.0', ([2.0], [5]),
         tf.SparseFeature('idx', 'value', tf.float32, 10)),
        # SparseFeature float no values.
        (',', ([], []),
         tf.SparseFeature('idx', 'value', tf.float32, 10))
    ]
    for csv_line, value, feature_spec in cases:
      schema = dataset_schema.from_feature_spec({'x': feature_spec})
      if isinstance(feature_spec, tf.SparseFeature):
        columns = [feature_spec.index_key, feature_spec.value_key]
      else:
        columns = 'x'
      coder = csv_coder.CsvCoder(columns, schema)
      self.assertEqual(
          coder.decode(csv_line), {'x': value},
          'While decoding {csv_line} with FeatureSpec {feature_spec}'.format(
              csv_line=csv_line, feature_spec=feature_spec))

  # Test successful encoding with a single column.
  def testEncode(self):
    cases = [
        # Fixedlen scalar numeric.
        ('12', 12, tf.FixedLenFeature(shape=[], dtype=tf.int32)),
        # Fixedlen 1-d vector numeric.
        ('12', [12], tf.FixedLenFeature(shape=[1], dtype=tf.int32)),
        # Fixedlen scalar text
        ('"this is a ,text"', 'this is a ,text',
         tf.FixedLenFeature(shape=[], dtype=tf.string))
    ]
    for expected_csv_line, value, feature_spec in cases:
      schema = dataset_schema.from_feature_spec({'x': feature_spec})
      if isinstance(feature_spec, tf.SparseFeature):
        columns = [feature_spec.index_key, feature_spec.value_key]
      else:
        columns = 'x'
      coder = csv_coder.CsvCoder(columns, schema)
      self.assertEqual(
          coder.encode({'x': value}), expected_csv_line,
          'While encoding {instance} with FeatureSpec {feature_spec}'.format(
              instance={'x': value}, feature_spec=feature_spec))

  # Test decode errors with a single column.
  def testDecodeErrors(self):
    cases = [
        # FixedLenFeature scalar numeric missing value.
        ('', ValueError, r'expected a value on column "x"',
         tf.FixedLenFeature(shape=[], dtype=tf.int32)),
        # FixedLenFeature 1-d vector numeric missing value.
        ('', ValueError, r'expected a value on column "x"',
         tf.FixedLenFeature(shape=[], dtype=tf.int32)),
        # FixedLenFeature scalar text missing value.
        ('', ValueError, r'expected a value on column "x"',
         tf.FixedLenFeature(shape=[], dtype=tf.string)),
        # SparseFeature with missing value but present index.
        ('5,', ValueError, r'expected a value in column "value"',
         tf.SparseFeature('idx', 'value', tf.float32, 10)),
        # SparseFeature with missing index but present value.
        (',2.0', ValueError, r'expected an index in column "idx"',
         tf.SparseFeature('idx', 'value', tf.float32, 10)),
        # SparseFeature with negative index.
        ('-1,2.0', ValueError, r'has index -1 out of range',
         tf.SparseFeature('idx', 'value', tf.float32, 10)),
        # SparseFeature with index equal to size.
        ('10,2.0', ValueError, r'has index 10 out of range',
         tf.SparseFeature('idx', 'value', tf.float32, 10)),
        # SparseFeature with index greater than size.
        ('11,2.0', ValueError, r'has index 11 out of range',
         tf.SparseFeature('idx', 'value', tf.float32, 10)),
        # FixedLenFeature with text missing value.
        ('test', ValueError, r'could not convert string to float: test',
         tf.FixedLenFeature(shape=[], dtype=tf.float32)),
    ]
    for csv_line, error_type, error_msg_re, feature_spec in cases:
      schema = dataset_schema.from_feature_spec({'x': feature_spec})
      if isinstance(feature_spec, tf.SparseFeature):
        columns = [feature_spec.index_key, feature_spec.value_key]
      else:
        columns = 'x'
      coder = csv_coder.CsvCoder(columns, schema)
      msg = 'While decoding {csv_line} with FeatureSpec {feature_spec}'.format(
          csv_line=csv_line, feature_spec=feature_spec)
      with self.assertRaisesRegexp(error_type, error_msg_re, msg=msg):
        coder.decode(csv_line)

  def test_missing_data(self):
    coder = csv_coder.CsvCoder(self._COLUMNS, self._INPUT_SCHEMA)

    data = '12,,female,1,89.0,12.0,14'
    with self.assertRaisesRegexp(ValueError,
                                 'expected a value on column "text1"'):
      coder.decode(data)

  def test_bad_row(self):
    coder = csv_coder.CsvCoder(self._COLUMNS, self._INPUT_SCHEMA)

    # The data has a more columns than expected.
    data = '12,"this is a ,text",female,1,89.0,12.0,"oh no, I\'m an error",14'
    with self.assertRaisesRegexp(Exception,
                                 'Columns do not match specified csv headers'):
      coder.decode(data)

    # The data has a fewer columns than expected.
    data = '12,"this is a ,text",female"'
    with self.assertRaisesRegexp(Exception,
                                 'Columns do not match specified csv headers'):
      coder.decode(data)

  def test_column_not_found(self):
    with self.assertRaisesRegexp(
        ValueError, 'Column not found: '):
      csv_coder.CsvCoder([], self._INPUT_SCHEMA)

  def test_picklable(self):
    encoded_data = '12,"this is a ,text",female,1,89.0,12.0,14'

    expected_decoded = {'category1': ['female'],
                        'numeric1': 12,
                        'numeric2': [89.0],
                        'numeric3': [14],
                        'text1': 'this is a ,text',
                        'y': ([12.0], [1])}

    coder = csv_coder.CsvCoder(self._COLUMNS, self._INPUT_SCHEMA)

    # Ensure we can pickle right away.
    coder = pickle.loads(pickle.dumps(coder))
    self._assert_encode_decode(coder, encoded_data, expected_decoded)

    #  And after use.
    coder = pickle.loads(pickle.dumps(coder))
    self._assert_encode_decode(coder, encoded_data, expected_decoded)

  def test_decode_errors(self):
    input_schema = dataset_schema.from_feature_spec({
        'b': tf.FixedLenFeature(shape=[], dtype=tf.float32),
        'a': tf.FixedLenFeature(shape=[], dtype=tf.string),
    })
    coder = csv_coder.CsvCoder(column_names=['a', 'b'], schema=input_schema)

    # Test bad csv.
    with self.assertRaisesRegexp(csv_coder.DecodeError,
                                 'string or Unicode object, int found'):
      coder.decode(123)

    # Test extra column.
    with self.assertRaisesRegexp(csv_coder.DecodeError,
                                 'Columns do not match specified csv headers'):
      coder.decode('1,2,')

    # Test missing column.
    with self.assertRaisesRegexp(csv_coder.DecodeError,
                                 'Columns do not match specified csv headers'):
      coder.decode('a_value')

    # Test empty row.
    with self.assertRaisesRegexp(csv_coder.DecodeError,
                                 'Columns do not match specified csv headers'):
      coder.decode('')


if __name__ == '__main__':
  unittest.main()
